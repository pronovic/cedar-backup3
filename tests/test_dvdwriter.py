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
# Purpose  : Tests DVD writer functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/writers/dvdwriter.py.

Code Coverage
=============

   This module contains individual tests for the public classes implemented in
   dvdwriter.py.

   Unfortunately, it's rather difficult to test this code in an automated
   fashion, even if you have access to a physical DVD writer drive.  It's even
   more difficult to test it if you are running on some build daemon (think of
   a Debian autobuilder) which can't be expected to have any hardware or any
   media that you could write to.  Because of this, there aren't any tests
   below that actually cause DVD media to be written to.

   As a compromise, complicated parts of the implementation are in terms of
   private static methods with well-defined behaviors.  Normally, I prefer to
   only test the public interface to class, but in this case, testing these few
   private methods will help give us some reasonable confidence in the code,
   even if we can't write a physical disc or can't run all of the tests.

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
   suite that has no surprising system, kernel or network requirements.  There
   are no special dependencies for these tests.

@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import os
import tempfile
import unittest

from CedarBackup3.testutil import buildPath, configureLogging, extractTar, findResources, removedir
from CedarBackup3.writers.dvdwriter import MEDIA_DVDPLUSR, MEDIA_DVDPLUSRW, DvdWriter, MediaCapacity, MediaDefinition

#######################################################################
# Module-wide configuration and constants
#######################################################################

GB44 = 4.4 * 1024.0 * 1024.0 * 1024.0  # 4.4 GB
GB44SECTORS = GB44 / 2048.0  # 4.4 GB in 2048-byte sectors

DATA_DIRS = [
    "./data",
    "./tests/data",
]
RESOURCES = [
    "tree9.tar.gz",
]


#######################################################################
# Test Case Classes
#######################################################################

############################
# TestMediaDefinition class
############################


class TestMediaDefinition(unittest.TestCase):

    """Tests for the MediaDefinition class."""

    @classmethod
    def setUpClass(cls):
        configureLogging()

    def testConstructor_001(self):
        """
        Test the constructor with an invalid media type.
        """
        self.assertRaises(ValueError, MediaDefinition, 100)

    def testConstructor_002(self):
        """
        Test the constructor with the ``MEDIA_DVDPLUSR`` media type.
        """
        media = MediaDefinition(MEDIA_DVDPLUSR)
        self.assertEqual(MEDIA_DVDPLUSR, media.mediaType)
        self.assertEqual(False, media.rewritable)
        self.assertEqual(GB44SECTORS, media.capacity)

    def testConstructor_003(self):
        """
        Test the constructor with the ``MEDIA_DVDPLUSRW`` media type.
        """
        media = MediaDefinition(MEDIA_DVDPLUSRW)
        self.assertEqual(MEDIA_DVDPLUSRW, media.mediaType)
        self.assertEqual(True, media.rewritable)
        self.assertEqual(GB44SECTORS, media.capacity)


##########################
# TestMediaCapacity class
##########################


class TestMediaCapacity(unittest.TestCase):

    """Tests for the MediaCapacity class."""

    @classmethod
    def setUpClass(cls):
        configureLogging()

    def testConstructor_001(self):
        """
        Test the constructor with valid, zero values
        """
        capacity = MediaCapacity(0.0, 0.0)
        self.assertEqual(0.0, capacity.bytesUsed)
        self.assertEqual(0.0, capacity.bytesAvailable)

    def testConstructor_002(self):
        """
        Test the constructor with valid, non-zero values.
        """
        capacity = MediaCapacity(1.1, 2.2)
        self.assertEqual(1.1, capacity.bytesUsed)
        self.assertEqual(2.2, capacity.bytesAvailable)

    def testConstructor_003(self):
        """
        Test the constructor with bytesUsed that is not a float.
        """
        self.assertRaises(ValueError, MediaCapacity, 0.0, "ken")

    def testConstructor_004(self):
        """
        Test the constructor with bytesAvailable that is not a float.
        """
        self.assertRaises(ValueError, MediaCapacity, "a", 0.0)


######################
# TestDvdWriter class
######################


class TestDvdWriter(unittest.TestCase):

    """Tests for the DvdWriter class."""

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
        removedir(self.tmpdir)

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

    def getFileContents(self, resource):
        """Gets contents of named resource as a list of strings."""
        path = self.resources[resource]
        with open(path) as f:
            return f.readlines()

    ###################
    # Test constructor
    ###################

    def testConstructor_001(self):
        """
        Test with an empty device.
        """
        self.assertRaises(ValueError, DvdWriter, None)

    def testConstructor_002(self):
        """
        Test with a device only.
        """
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual(None, dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(None, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSRW, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_003(self):
        """
        Test with a device and valid SCSI id.
        """
        dvdwriter = DvdWriter("/dev/dvd", scsiId="ATA:1,0,0", unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual("ATA:1,0,0", dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(None, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSRW, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_004(self):
        """
        Test with a device and valid drive speed.
        """
        dvdwriter = DvdWriter("/dev/dvd", driveSpeed=3, unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual(None, dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(3, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSRW, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_005(self):
        """
        Test with a device with media type MEDIA_DVDPLUSR.
        """
        dvdwriter = DvdWriter("/dev/dvd", mediaType=MEDIA_DVDPLUSR, unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual(None, dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(None, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSR, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_006(self):
        """
        Test with a device with media type MEDIA_DVDPLUSRW.
        """
        dvdwriter = DvdWriter("/dev/dvd", mediaType=MEDIA_DVDPLUSR, unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual(None, dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(None, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSR, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_007(self):
        """
        Test with a device and invalid SCSI id.
        """
        dvdwriter = DvdWriter("/dev/dvd", scsiId="00000000", unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual("00000000", dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(None, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSRW, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_008(self):
        """
        Test with a device and invalid drive speed.
        """
        self.assertRaises(ValueError, DvdWriter, "/dev/dvd", driveSpeed="KEN", unittest=True)

    def testConstructor_009(self):
        """
        Test with a device and invalid media type.
        """
        self.assertRaises(ValueError, DvdWriter, "/dev/dvd", mediaType=999, unittest=True)

    def testConstructor_010(self):
        """
        Test with all valid parameters, but no device, unittest=True.
        """
        self.assertRaises(ValueError, DvdWriter, None, "ATA:1,0,0", 1, MEDIA_DVDPLUSRW, unittest=True)

    def testConstructor_011(self):
        """
        Test with all valid parameters, but no device, unittest=False.
        """
        self.assertRaises(ValueError, DvdWriter, None, "ATA:1,0,0", 1, MEDIA_DVDPLUSRW, unittest=False)

    def testConstructor_012(self):
        """
        Test with all valid parameters, and an invalid device (not absolute path), unittest=True.
        """
        self.assertRaises(ValueError, DvdWriter, "dev/dvd", "ATA:1,0,0", 1, MEDIA_DVDPLUSRW, unittest=True)

    def testConstructor_013(self):
        """
        Test with all valid parameters, and an invalid device (not absolute path), unittest=False.
        """
        self.assertRaises(ValueError, DvdWriter, "dev/dvd", "ATA:1,0,0", 1, MEDIA_DVDPLUSRW, unittest=False)

    def testConstructor_014(self):
        """
        Test with all valid parameters, and an invalid device (path does not exist), unittest=False.
        """
        self.assertRaises(ValueError, DvdWriter, "/dev/bogus", "ATA:1,0,0", 1, MEDIA_DVDPLUSRW, unittest=False)

    def testConstructor_015(self):
        """
        Test with all valid parameters.
        """
        dvdwriter = DvdWriter("/dev/dvd", "ATA:1,0,0", 1, MEDIA_DVDPLUSR, noEject=False, unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual("ATA:1,0,0", dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(1, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSR, dvdwriter.media.mediaType)
        self.assertEqual(True, dvdwriter.deviceHasTray)
        self.assertEqual(True, dvdwriter.deviceCanEject)

    def testConstructor_016(self):
        """
        Test with all valid parameters.
        """
        dvdwriter = DvdWriter("/dev/dvd", "ATA:1,0,0", 1, MEDIA_DVDPLUSR, noEject=True, unittest=True)
        self.assertEqual("/dev/dvd", dvdwriter.device)
        self.assertEqual("ATA:1,0,0", dvdwriter.scsiId)
        self.assertEqual("/dev/dvd", dvdwriter.hardwareId)
        self.assertEqual(1, dvdwriter.driveSpeed)
        self.assertEqual(MEDIA_DVDPLUSR, dvdwriter.media.mediaType)
        self.assertEqual(False, dvdwriter.deviceHasTray)
        self.assertEqual(False, dvdwriter.deviceCanEject)

    ######################
    # Test isRewritable()
    ######################

    def testIsRewritable_001(self):
        """
        Test with MEDIA_DVDPLUSR.
        """
        dvdwriter = DvdWriter("/dev/dvd", mediaType=MEDIA_DVDPLUSR, unittest=True)
        self.assertEqual(False, dvdwriter.isRewritable())

    def testIsRewritable_002(self):
        """
        Test with MEDIA_DVDPLUSRW.
        """
        dvdwriter = DvdWriter("/dev/dvd", mediaType=MEDIA_DVDPLUSRW, unittest=True)
        self.assertEqual(True, dvdwriter.isRewritable())

    #########################
    # Test initializeImage()
    #########################

    def testInitializeImage_001(self):
        """
        Test with newDisc=False, tmpdir=None.
        """
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        self.assertEqual(False, dvdwriter._image.newDisc)
        self.assertEqual(None, dvdwriter._image.tmpdir)
        self.assertEqual({}, dvdwriter._image.entries)

    def testInitializeImage_002(self):
        """
        Test with newDisc=True, tmpdir not None.
        """
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(True, "/path/to/somewhere")
        self.assertEqual(True, dvdwriter._image.newDisc)
        self.assertEqual("/path/to/somewhere", dvdwriter._image.tmpdir)
        self.assertEqual({}, dvdwriter._image.entries)

    #######################
    # Test addImageEntry()
    #######################

    def testAddImageEntry_001(self):
        """
        Add a valid path with no graft point, before calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "dir002"])
        self.assertTrue(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        self.assertRaises(ValueError, dvdwriter.addImageEntry, path, None)

    def testAddImageEntry_002(self):
        """
        Add a valid path with a graft point, before calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "dir002"])
        self.assertTrue(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        self.assertRaises(ValueError, dvdwriter.addImageEntry, path, "ken")

    def testAddImageEntry_003(self):
        """
        Add a non-existent path with no graft point, before calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "bogus"])
        self.assertFalse(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        self.assertRaises(ValueError, dvdwriter.addImageEntry, path, None)

    def testAddImageEntry_004(self):
        """
        Add a non-existent path with a graft point, before calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "bogus"])
        self.assertFalse(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        self.assertRaises(ValueError, dvdwriter.addImageEntry, path, "ken")

    def testAddImageEntry_005(self):
        """
        Add a valid path with no graft point, after calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "dir002"])
        self.assertTrue(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        dvdwriter.addImageEntry(path, None)
        self.assertEqual({path: None}, dvdwriter._image.entries)

    def testAddImageEntry_006(self):
        """
        Add a valid path with a graft point, after calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "dir002"])
        self.assertTrue(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        dvdwriter.addImageEntry(path, "ken")
        self.assertEqual({path: "ken"}, dvdwriter._image.entries)

    def testAddImageEntry_007(self):
        """
        Add a non-existent path with no graft point, after calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "bogus"])
        self.assertFalse(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        self.assertRaises(ValueError, dvdwriter.addImageEntry, path, None)

    def testAddImageEntry_008(self):
        """
        Add a non-existent path with a graft point, after calling initializeImage().
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "bogus"])
        self.assertFalse(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        self.assertRaises(ValueError, dvdwriter.addImageEntry, path, "ken")

    def testAddImageEntry_009(self):
        """
        Add the same path several times.
        """
        self.extractTar("tree9")
        path = self.buildPath(["tree9", "dir002"])
        self.assertTrue(os.path.exists(path))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        dvdwriter.addImageEntry(path, "ken")
        self.assertEqual({path: "ken"}, dvdwriter._image.entries)
        dvdwriter.addImageEntry(path, "ken")
        self.assertEqual({path: "ken"}, dvdwriter._image.entries)
        dvdwriter.addImageEntry(path, "ken")
        self.assertEqual({path: "ken"}, dvdwriter._image.entries)
        dvdwriter.addImageEntry(path, "ken")
        self.assertEqual({path: "ken"}, dvdwriter._image.entries)

    def testAddImageEntry_010(self):
        """
        Add several paths.
        """
        self.extractTar("tree9")
        path1 = self.buildPath(["tree9", "dir001"])
        path2 = self.buildPath(["tree9", "dir002"])
        path3 = self.buildPath(["tree9", "dir001", "dir001"])
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
        self.assertTrue(os.path.exists(path3))
        dvdwriter = DvdWriter("/dev/dvd", unittest=True)
        dvdwriter.initializeImage(False, None)
        dvdwriter.addImageEntry(path1, None)
        self.assertEqual({path1: None}, dvdwriter._image.entries)
        dvdwriter.addImageEntry(path2, "ken")
        self.assertEqual({path1: None, path2: "ken"}, dvdwriter._image.entries)
        dvdwriter.addImageEntry(path3, "another")
        self.assertEqual({path1: None, path2: "ken", path3: "another"}, dvdwriter._image.entries)

    ############################
    # Test _searchForOverburn()
    ############################

    def testSearchForOverburn_001(self):
        """
        Test with output=None.
        """
        output = None
        DvdWriter._searchForOverburn(output)  # no exception should be thrown

    def testSearchForOverburn_002(self):
        """
        Test with output=[].
        """
        output = []
        DvdWriter._searchForOverburn(output)  # no exception should be thrown

    def testSearchForOverburn_003(self):
        """
        Test with one-line output, not containing the pattern.
        """
        output = [
            "This line does not contain the pattern",
        ]
        DvdWriter._searchForOverburn(output)  # no exception should be thrown
        output = [
            ":-( /dev/cdrom: blocks are free, to be written!",
        ]
        DvdWriter._searchForOverburn(output)  # no exception should be thrown
        output = [
            ":-) /dev/cdrom: 89048 blocks are free, 2033746 to be written!",
        ]
        DvdWriter._searchForOverburn(output)  # no exception should be thrown
        output = [
            ":-( /dev/cdrom: 894048blocks are free, 2033746to be written!",
        ]
        DvdWriter._searchForOverburn(output)  # no exception should be thrown

    def testSearchForOverburn_004(self):
        """
        Test with one-line output(s), containing the pattern.
        """
        output = [
            ":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)
        output = [
            ":-( /dev/cdrom: XXXX blocks are free, XXXX to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)
        output = [
            ":-( /dev/cdrom: 1 blocks are free, 1 to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)
        output = [
            ":-( /dev/cdrom: 0 blocks are free, 0 to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)
        output = [
            ":-( /dev/dvd: 0 blocks are free, 0 to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)
        output = [
            ":-( /dev/writer: 0 blocks are free, 0 to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)
        output = [
            ":-( bogus: 0 blocks are free, 0 to be written!",
        ]
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)

    def testSearchForOverburn_005(self):
        """
        Test with multi-line output, not containing the pattern.
        """
        output = []
        output.append(
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'"
        )
        output.append("Rock Ridge signatures found")
        output.append("Using THE_K000 for  music4/The_Kings_Singers (The_Kingston_Trio)")
        output.append(
            "Using COCKT000 for music/Various_Artists/Cocktail_Classics_-_Beethovens_Fifth_and_Others (Cocktail_Classics_-_Pachelbels_Canon_and_Others)"
        )
        output.append(
            "Using THE_V000 for  music/Brahms/The_Violin_Sonatas (The_Viola_Sonatas) Using COMPL000 for  music/Gershwin/Complete_Gershwin_2 (Complete_Gershwin_1)"
        )
        output.append(
            "Using SELEC000.MP3;1 for music/Marquette_Chorus/Selected_Christmas_Carols_For_Double_Choir.mp3 (Selected_Choruses_from_The_Lark.mp3)"
        )
        output.append(
            "Using SELEC001.MP3;1 for music/Marquette_Chorus/Selected_Choruses_from_The_Lark.mp3 (Selected_Choruses_from_Messiah.mp3)"
        )
        output.append(
            "Using IN_TH000.MP3;1 for  music/Marquette_Chorus/In_the_Bleak_Midwinter.mp3 (In_the_Beginning.mp3) Using AFRIC000.MP3;1 for  music/Marquette_Chorus/African_Noel-tb.mp3 (African_Noel-satb.mp3)"
        )
        DvdWriter._searchForOverburn(output)  # no exception should be thrown")

    def testSearchForOverburn_006(self):
        """
        Test with multi-line output, containing the pattern at the top.
        """
        output = []
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'"
        )
        output.append("Rock Ridge signatures found")
        output.append("Using THE_K000 for  music4/The_Kings_Singers (The_Kingston_Trio)")
        output.append(
            "Using COCKT000 for music/Various_Artists/Cocktail_Classics_-_Beethovens_Fifth_and_Others (Cocktail_Classics_-_Pachelbels_Canon_and_Others)"
        )
        output.append(
            "Using THE_V000 for  music/Brahms/The_Violin_Sonatas (The_Viola_Sonatas) Using COMPL000 for  music/Gershwin/Complete_Gershwin_2 (Complete_Gershwin_1)"
        )
        output.append(
            "Using SELEC000.MP3;1 for music/Marquette_Chorus/Selected_Christmas_Carols_For_Double_Choir.mp3 (Selected_Choruses_from_The_Lark.mp3)"
        )
        output.append(
            "Using SELEC001.MP3;1 for music/Marquette_Chorus/Selected_Choruses_from_The_Lark.mp3 (Selected_Choruses_from_Messiah.mp3)"
        )
        output.append(
            "Using IN_TH000.MP3;1 for  music/Marquette_Chorus/In_the_Bleak_Midwinter.mp3 (In_the_Beginning.mp3) Using AFRIC000.MP3;1 for  music/Marquette_Chorus/African_Noel-tb.mp3 (African_Noel-satb.mp3)"
        )
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)

    def testSearchForOverburn_007(self):
        """
        Test with multi-line output, containing the pattern at the bottom.
        """
        output = []
        output.append(
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'"
        )
        output.append("Rock Ridge signatures found")
        output.append("Using THE_K000 for  music4/The_Kings_Singers (The_Kingston_Trio)")
        output.append(
            "Using COCKT000 for music/Various_Artists/Cocktail_Classics_-_Beethovens_Fifth_and_Others (Cocktail_Classics_-_Pachelbels_Canon_and_Others)"
        )
        output.append(
            "Using THE_V000 for  music/Brahms/The_Violin_Sonatas (The_Viola_Sonatas) Using COMPL000 for  music/Gershwin/Complete_Gershwin_2 (Complete_Gershwin_1)"
        )
        output.append(
            "Using SELEC000.MP3;1 for music/Marquette_Chorus/Selected_Christmas_Carols_For_Double_Choir.mp3 (Selected_Choruses_from_The_Lark.mp3)"
        )
        output.append(
            "Using SELEC001.MP3;1 for music/Marquette_Chorus/Selected_Choruses_from_The_Lark.mp3 (Selected_Choruses_from_Messiah.mp3)"
        )
        output.append(
            "Using IN_TH000.MP3;1 for  music/Marquette_Chorus/In_the_Bleak_Midwinter.mp3 (In_the_Beginning.mp3) Using AFRIC000.MP3;1 for  music/Marquette_Chorus/African_Noel-tb.mp3 (African_Noel-satb.mp3)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)

    def testSearchForOverburn_008(self):
        """
        Test with multi-line output, containing the pattern in the middle.
        """
        output = []
        output.append(
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'"
        )
        output.append("Rock Ridge signatures found")
        output.append("Using THE_K000 for  music4/The_Kings_Singers (The_Kingston_Trio)")
        output.append(
            "Using COCKT000 for music/Various_Artists/Cocktail_Classics_-_Beethovens_Fifth_and_Others (Cocktail_Classics_-_Pachelbels_Canon_and_Others)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Using THE_V000 for  music/Brahms/The_Violin_Sonatas (The_Viola_Sonatas) Using COMPL000 for  music/Gershwin/Complete_Gershwin_2 (Complete_Gershwin_1)"
        )
        output.append(
            "Using SELEC000.MP3;1 for music/Marquette_Chorus/Selected_Christmas_Carols_For_Double_Choir.mp3 (Selected_Choruses_from_The_Lark.mp3)"
        )
        output.append(
            "Using SELEC001.MP3;1 for music/Marquette_Chorus/Selected_Choruses_from_The_Lark.mp3 (Selected_Choruses_from_Messiah.mp3)"
        )
        output.append(
            "Using IN_TH000.MP3;1 for  music/Marquette_Chorus/In_the_Bleak_Midwinter.mp3 (In_the_Beginning.mp3) Using AFRIC000.MP3;1 for  music/Marquette_Chorus/African_Noel-tb.mp3 (African_Noel-satb.mp3)"
        )
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)

    def testSearchForOverburn_009(self):
        """
        Test with multi-line output, containing the pattern several times.
        """
        output = []
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append("Rock Ridge signatures found")
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append("Using THE_K000 for  music4/The_Kings_Singers (The_Kingston_Trio)")
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Using COCKT000 for music/Various_Artists/Cocktail_Classics_-_Beethovens_Fifth_and_Others (Cocktail_Classics_-_Pachelbels_Canon_and_Others)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Using THE_V000 for  music/Brahms/The_Violin_Sonatas (The_Viola_Sonatas) Using COMPL000 for  music/Gershwin/Complete_Gershwin_2 (Complete_Gershwin_1)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Using SELEC000.MP3;1 for music/Marquette_Chorus/Selected_Christmas_Carols_For_Double_Choir.mp3 (Selected_Choruses_from_The_Lark.mp3)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Using SELEC001.MP3;1 for music/Marquette_Chorus/Selected_Choruses_from_The_Lark.mp3 (Selected_Choruses_from_Messiah.mp3)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(
            "Using IN_TH000.MP3;1 for  music/Marquette_Chorus/In_the_Bleak_Midwinter.mp3 (In_the_Beginning.mp3) Using AFRIC000.MP3;1 for  music/Marquette_Chorus/African_Noel-tb.mp3 (African_Noel-satb.mp3)"
        )
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        output.append(":-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!")
        self.assertRaises(IOError, DvdWriter._searchForOverburn, output)

    ###########################
    # Test _parseSectorsUsed()
    ###########################

    def testParseSectorsUsed_001(self):
        """
        Test with output=None.
        """
        output = None
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(0.0, sectorsUsed)

    def testParseSectorsUsed_002(self):
        """
        Test with output=[].
        """
        output = []
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(0.0, sectorsUsed)

    def testParseSectorsUsed_003(self):
        """
        Test with one-line output, not containing the pattern.
        """
        output = [
            "This line does not contain the pattern",
        ]
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(0.0, sectorsUsed)

    def testParseSectorsUsed_004(self):
        """
        Test with one-line output(s), containing the pattern.
        """
        output = [
            "'seek=10'",
        ]
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(10.0 * 16.0, sectorsUsed)

        output = [
            "'    seek=    10     '",
        ]
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(10.0 * 16.0, sectorsUsed)

        output = [
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'",
        ]
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(87566 * 16.0, sectorsUsed)

    def testParseSectorsUsed_005(self):
        """
        Test with real growisofs output.
        """
        output = []
        output.append(
            "Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'"
        )
        output.append("Rock Ridge signatures found")
        output.append("Using THE_K000 for  music4/The_Kings_Singers (The_Kingston_Trio)")
        output.append(
            "Using COCKT000 for music/Various_Artists/Cocktail_Classics_-_Beethovens_Fifth_and_Others (Cocktail_Classics_-_Pachelbels_Canon_and_Others)"
        )
        output.append(
            "Using THE_V000 for  music/Brahms/The_Violin_Sonatas (The_Viola_Sonatas) Using COMPL000 for  music/Gershwin/Complete_Gershwin_2 (Complete_Gershwin_1)"
        )
        output.append(
            "Using SELEC000.MP3;1 for music/Marquette_Chorus/Selected_Christmas_Carols_For_Double_Choir.mp3 (Selected_Choruses_from_The_Lark.mp3)"
        )
        output.append(
            "Using SELEC001.MP3;1 for music/Marquette_Chorus/Selected_Choruses_from_The_Lark.mp3 (Selected_Choruses_from_Messiah.mp3)"
        )
        output.append(
            "Using IN_TH000.MP3;1 for  music/Marquette_Chorus/In_the_Bleak_Midwinter.mp3 (In_the_Beginning.mp3) Using AFRIC000.MP3;1 for  music/Marquette_Chorus/African_Noel-tb.mp3 (African_Noel-satb.mp3)"
        )
        sectorsUsed = DvdWriter._parseSectorsUsed(output)
        self.assertEqual(87566 * 16.0, sectorsUsed)

    #########################
    # Test _buildWriteArgs()
    #########################

    def testBuildWriteArgs_001(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath=None, entries=None, mediaLabel=None,dryRun=False.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = None
        entries = None
        mediaLabel = None
        dryRun = False
        self.assertRaises(
            ValueError, DvdWriter._buildWriteArgs, newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun
        )

    def testBuildWriteArgs_002(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath=None, entries=None, mediaLabel=None, dryRun=True.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = None
        entries = None
        mediaLabel = None
        dryRun = True
        self.assertRaises(
            ValueError, DvdWriter._buildWriteArgs, newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun
        )

    def testBuildWriteArgs_003(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=False.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-M",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_004(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=True.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-M",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_005(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=False.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-Z",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_006(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=True.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-Z",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_007(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=1,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=False.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = 1
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-speed=1",
            "-M",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_008(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=2,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=True.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = 2
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-speed=2",
            "-M",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_009(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=3,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=False.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = 3
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-speed=3",
            "-Z",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_010(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=4,
        imagePath="/path/to/image", entries=None, mediaLabel=None, dryRun=True.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = 4
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-speed=4",
            "-Z",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_011(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath=None, entries=<one>, mediaLabel=None, dryRun=False.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = None
        entries = {
            "path1": None,
        }
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-M",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "path1",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_012(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath=None, entries=<one>, mediaLabel=None, dryRun=True.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = None
        entries = {
            "path1": None,
        }
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-M",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "path1",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_013(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath=None, entries=<several>, mediaLabel=None, dryRun=False.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = None
        entries = {
            "path1": None,
            "path2": "graft2",
            "path3": "/path/to/graft3",
        }
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-Z",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "path1",
            "graft2/=path2",
            "path/to/graft3/=path3",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_014(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=None,
        imagePath=None, entries=<several>, mediaLabel=None, dryRun=True.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = None
        imagePath = None
        entries = {
            "path1": None,
            "path2": "graft2",
            "path3": "/path/to/graft3",
        }
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-Z",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "path1",
            "graft2/=path2",
            "path/to/graft3/=path3",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_015(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=1,
        imagePath=None, entries=<several>, mediaLabel=None, dryRun=False.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = 1
        imagePath = None
        entries = {
            "path1": None,
            "path2": "graft2",
        }
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-speed=1",
            "-M",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "path1",
            "graft2/=path2",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_016(self):
        """
        Test with newDisc=False, hardwareId="/dev/dvd", driveSpeed=2,
        imagePath=None, entries=<several>, mediaLabel=None, dryRun=True.
        """
        newDisc = False
        hardwareId = "/dev/dvd"
        driveSpeed = 2
        imagePath = None
        entries = {
            "path1": None,
            "path2": "graft2",
        }
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-speed=2",
            "-M",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "path1",
            "graft2/=path2",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_017(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=3,
        imagePath=None, entries=<several>, mediaLabel=None, dryRun=False.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = 3
        imagePath = None
        entries = {
            "path1": None,
            "/path/to/path2": None,
            "/path/to/path3/": "/path/to/graft3/",
        }
        mediaLabel = None
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-speed=3",
            "-Z",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "/path/to/path2",
            "path/to/graft3/=/path/to/path3/",
            "path1",
        ]  # sorted order
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_018(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=4,
        imagePath=None, entries=<several>, mediaLabel=None, dryRun=True.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = 4
        imagePath = None
        entries = {
            "path1": None,
            "/path/to/path2": None,
            "/path/to/path3/": "/path/to/graft3/",
        }
        mediaLabel = None
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-speed=4",
            "-Z",
            "/dev/dvd",
            "-r",
            "-graft-points",
            "/path/to/path2",
            "path/to/graft3/=/path/to/path3/",
            "path1",
        ]  # sorted order
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_019(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=3,
        imagePath="/path/to/image", entries=None, mediaLabel="BACKUP", dryRun=False.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = 3
        imagePath = "/path/to/image"
        entries = None
        mediaLabel = "BACKUP"
        dryRun = False
        expected = [
            "-use-the-force-luke=tty",
            "-speed=3",
            "-Z",
            "/dev/dvd=/path/to/image",
        ]
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)

    def testBuildWriteArgs_020(self):
        """
        Test with newDisc=True, hardwareId="/dev/dvd", driveSpeed=4,
        imagePath=None, entries=<several>, mediaLabel="BACKUP", dryRun=True.
        """
        newDisc = True
        hardwareId = "/dev/dvd"
        driveSpeed = 4
        imagePath = None
        entries = {
            "path1": None,
            "/path/to/path2": None,
            "/path/to/path3/": "/path/to/graft3/",
        }
        mediaLabel = "BACKUP"
        dryRun = True
        expected = [
            "-use-the-force-luke=tty",
            "-dry-run",
            "-speed=4",
            "-Z",
            "/dev/dvd",
            "-V",
            "BACKUP",
            "-r",
            "-graft-points",
            "/path/to/path2",
            "path/to/graft3/=/path/to/path3/",
            "path1",
        ]  # sorted order
        actual = DvdWriter._buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel, dryRun)
        self.assertEqual(actual, expected)
