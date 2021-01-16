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
# Copyright (c) 2007-2008,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides functionality related to DVD writer devices.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides functionality related to DVD writer devices.

Module Attributes
=================

Attributes:
   MEDIA_DVDPLUSR: Constant representing DVD+R media
   MEDIA_DVDPLUSRW: Constant representing DVD+RW media

:author: Kenneth J. Pronovici <pronovic@ieee.org>
:author: Dmitry Rutsky <rutsky@inbox.ru>
"""

########################################################################
# Imported modules
########################################################################

import logging
import os
import re
import tempfile
import time

from CedarBackup3.util import (
    UNIT_BYTES,
    UNIT_GBYTES,
    UNIT_SECTORS,
    convertSize,
    displayBytes,
    encodePath,
    executeCommand,
    resolveCommand,
)
from CedarBackup3.writers.util import IsoImage, validateDevice, validateDriveSpeed

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.writers.dvdwriter")

MEDIA_DVDPLUSR = 1
MEDIA_DVDPLUSRW = 2

GROWISOFS_COMMAND = ["growisofs"]
EJECT_COMMAND = ["eject"]


########################################################################
# MediaDefinition class definition
########################################################################


class MediaDefinition(object):

    """
    Class encapsulating information about DVD media definitions.

    The following media types are accepted:

          - ``MEDIA_DVDPLUSR``: DVD+R media (4.4 GB capacity)
          - ``MEDIA_DVDPLUSRW``: DVD+RW media (4.4 GB capacity)

    Note that the capacity attribute returns capacity in terms of ISO sectors
    (``util.ISO_SECTOR_SIZE)``.  This is for compatibility with the CD writer
    functionality.

    The capacities are 4.4 GB because Cedar Backup deals in "true" gigabytes
    of 1024*1024*1024 bytes per gigabyte.

    """

    def __init__(self, mediaType):
        """
        Creates a media definition for the indicated media type.
        Args:
           mediaType: Type of the media, as discussed above
        Raises:
           ValueError: If the media type is unknown or unsupported
        """
        self._mediaType = None
        self._rewritable = False
        self._capacity = 0.0
        self._setValues(mediaType)

    def _setValues(self, mediaType):
        """
        Sets values based on media type.
        Args:
           mediaType: Type of the media, as discussed above
        Raises:
           ValueError: If the media type is unknown or unsupported
        """
        if mediaType not in [MEDIA_DVDPLUSR, MEDIA_DVDPLUSRW]:
            raise ValueError("Invalid media type %d." % mediaType)
        self._mediaType = mediaType
        if self._mediaType == MEDIA_DVDPLUSR:
            self._rewritable = False
            self._capacity = convertSize(4.4, UNIT_GBYTES, UNIT_SECTORS)  # 4.4 "true" GB = 4.7 "marketing" GB
        elif self._mediaType == MEDIA_DVDPLUSRW:
            self._rewritable = True
            self._capacity = convertSize(4.4, UNIT_GBYTES, UNIT_SECTORS)  # 4.4 "true" GB = 4.7 "marketing" GB

    def _getMediaType(self):
        """
        Property target used to get the media type value.
        """
        return self._mediaType

    def _getRewritable(self):
        """
        Property target used to get the rewritable flag value.
        """
        return self._rewritable

    def _getCapacity(self):
        """
        Property target used to get the capacity value.
        """
        return self._capacity

    mediaType = property(_getMediaType, None, None, doc="Configured media type.")
    rewritable = property(_getRewritable, None, None, doc="Boolean indicating whether the media is rewritable.")
    capacity = property(_getCapacity, None, None, doc="Total capacity of media in 2048-byte sectors.")


########################################################################
# MediaCapacity class definition
########################################################################


class MediaCapacity(object):

    """
    Class encapsulating information about DVD media capacity.

    Space used and space available do not include any information about media
    lead-in or other overhead.

    """

    def __init__(self, bytesUsed, bytesAvailable):
        """
        Initializes a capacity object.

        Raises:
           ValueError: If the bytes used and available values are not floats
        """
        self._bytesUsed = float(bytesUsed)
        self._bytesAvailable = float(bytesAvailable)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return "utilized %s of %s (%.2f%%)" % (displayBytes(self.bytesUsed), displayBytes(self.totalCapacity), self.utilized)

    def _getBytesUsed(self):
        """
        Property target used to get the bytes-used value.
        """
        return self._bytesUsed

    def _getBytesAvailable(self):
        """
        Property target available to get the bytes-available value.
        """
        return self._bytesAvailable

    def _getTotalCapacity(self):
        """
        Property target to get the total capacity (used + available).
        """
        return self.bytesUsed + self.bytesAvailable

    def _getUtilized(self):
        """
        Property target to get the percent of capacity which is utilized.
        """
        if self.bytesAvailable <= 0.0:
            return 100.0
        elif self.bytesUsed <= 0.0:
            return 0.0
        return (self.bytesUsed / self.totalCapacity) * 100.0

    bytesUsed = property(_getBytesUsed, None, None, doc="Space used on disc, in bytes.")
    bytesAvailable = property(_getBytesAvailable, None, None, doc="Space available on disc, in bytes.")
    totalCapacity = property(_getTotalCapacity, None, None, doc="Total capacity of the disc, in bytes.")
    utilized = property(_getUtilized, None, None, "Percentage of the total capacity which is utilized.")


########################################################################
# _ImageProperties class definition
########################################################################


class _ImageProperties(object):
    """
    Simple value object to hold image properties for ``DvdWriter``.
    """

    def __init__(self):
        self.newDisc = False
        self.tmpdir = None
        self.mediaLabel = None
        self.entries = None  # dict mapping path to graft point


########################################################################
# DvdWriter class definition
########################################################################


class DvdWriter(object):

    ######################
    # Class documentation
    ######################

    """
    Class representing a device that knows how to write some kinds of DVD media.

    **Summary**

    This is a class representing a device that knows how to write some kinds
    of DVD media.  It provides common operations for the device, such as
    ejecting the media and writing data to the media.

    This class is implemented in terms of the ``eject`` and ``growisofs``
    utilities, all of which should be available on most UN*X platforms.

    **Image Writer Interface**

    The following methods make up the "image writer" interface shared
    with other kinds of writers::

       __init__
       initializeImage()
       addImageEntry()
       writeImage()
       setImageNewDisc()
       retrieveCapacity()
       getEstimatedImageSize()

    Only these methods will be used by other Cedar Backup functionality
    that expects a compatible image writer.

    The media attribute is also assumed to be available.

    Unlike the ``CdWriter``, the ``DvdWriter`` can only operate in terms of
    filesystem devices, not SCSI devices.  So, although the constructor
    interface accepts a SCSI device parameter for the sake of compatibility,
    it's not used.

    **Media Types**

    This class knows how to write to DVD+R and DVD+RW media, represented
    by the following constants:

       - ``MEDIA_DVDPLUSR``: DVD+R media (4.4 GB capacity)
       - ``MEDIA_DVDPLUSRW``: DVD+RW media (4.4 GB capacity)

    The difference is that DVD+RW media can be rewritten, while DVD+R media
    cannot be (although at present, ``DvdWriter`` does not really
    differentiate between rewritable and non-rewritable media).

    The capacities are 4.4 GB because Cedar Backup deals in "true" gigabytes
    of 1024*1024*1024 bytes per gigabyte.

    The underlying ``growisofs`` utility does support other kinds of media
    (including DVD-R, DVD-RW and BlueRay) which work somewhat differently
    than standard DVD+R and DVD+RW media.  I don't support these other kinds
    of media because I haven't had any opportunity to work with them.  The
    same goes for dual-layer media of any type.

    **Device Attributes vs. Media Attributes**

    As with the cdwriter functionality, a given dvdwriter instance has two
    different kinds of attributes associated with it.  I call these device
    attributes and media attributes.

    Device attributes are things which can be determined without looking at
    the media.  Media attributes are attributes which vary depending on the
    state of the media.  In general, device attributes are available via
    instance variables and are constant over the life of an object, while
    media attributes can be retrieved through method calls.

    Compared to cdwriters, dvdwriters have very few attributes.  This is due
    to differences between the way ``growisofs`` works relative to
    ``cdrecord``.

    **Media Capacity**

    One major difference between the ``cdrecord``/``mkisofs`` utilities used by
    the cdwriter class and the ``growisofs`` utility used here is that the
    process of estimating remaining capacity and image size is more
    straightforward with ``cdrecord``/``mkisofs`` than with ``growisofs``.

    In this class, remaining capacity is calculated by asking doing a dry run
    of ``growisofs`` and grabbing some information from the output of that
    command.  Image size is estimated by asking the ``IsoImage`` class for an
    estimate and then adding on a "fudge factor" determined through
    experimentation.

    **Testing**

    It's rather difficult to test this code in an automated fashion, even if
    you have access to a physical DVD writer drive.  It's even more difficult
    to test it if you are running on some build daemon (think of a Debian
    autobuilder) which can't be expected to have any hardware or any media
    that you could write to.

    Because of this, some of the implementation below is in terms of static
    methods that are supposed to take defined actions based on their
    arguments.  Public methods are then implemented in terms of a series of
    calls to simplistic static methods.  This way, we can test as much as
    possible of the "difficult" functionality via testing the static methods,
    while hoping that if the static methods are called appropriately, things
    will work properly.  It's not perfect, but it's much better than no
    testing at all.

    """

    ##############
    # Constructor
    ##############

    def __init__(
        self,
        device,
        scsiId=None,
        driveSpeed=None,
        mediaType=MEDIA_DVDPLUSRW,
        noEject=False,
        refreshMediaDelay=0,
        ejectDelay=0,
        unittest=False,
    ):
        """
        Initializes a DVD writer object.

        Since ``growisofs`` can only address devices using the device path (i.e.
        ``/dev/dvd``), the hardware id will always be set based on the device.  If
        passed in, it will be saved for reference purposes only.

        We have no way to query the device to ask whether it has a tray or can be
        safely opened and closed.  So, the ``noEject`` flag is used to set these
        values.  If ``noEject=False``, then we assume a tray exists and open/close
        is safe.  If ``noEject=True``, then we assume that there is no tray and
        open/close is not safe.

        The SCSI id, if provided, is in the form ``[<method>:]scsibus,target,lun``.

        *Note:* The ``unittest`` parameter should never be set to ``True``
        outside of Cedar Backup code.  It is intended for use in unit testing
        Cedar Backup internals and has no other sensible purpose.

        Args:
           device: Absolute path to the writer filesystem device, like ``/dev/dvd``
           scsiId: SCSI id for the device (optional, for reference only)
           driveSpeed: Speed at which the drive writes, like 2 for a 2x device, or None for device default
           mediaType: Type of the media that is assumed to be in the drive
           noEject (Boolean true/false): Tells Cedar Backup that the device cannot safely be ejected
           refreshMediaDelay (Integer >= 0): Refresh media delay to use, if any
           ejectDelay (Integer >= 0): Eject delay to use, if any
           unittest (Boolean true/false): Turns off certain validations, for use in unit testing
        Raises:
           ValueError: If the device is not valid for some reason
           ValueError: If the SCSI id is not in a valid form
           ValueError: If the drive speed is not an integer >= 1
        """
        if scsiId is not None:
            logger.warning("SCSI id [%s] will be ignored by DvdWriter.", scsiId)
        self._image = None  # optionally filled in by initializeImage()
        self._device = validateDevice(device, unittest)
        self._scsiId = scsiId  # not validated, because it's just for reference
        self._driveSpeed = validateDriveSpeed(driveSpeed)
        self._media = MediaDefinition(mediaType)
        self._refreshMediaDelay = refreshMediaDelay
        self._ejectDelay = ejectDelay
        if noEject:
            self._deviceHasTray = False
            self._deviceCanEject = False
        else:
            self._deviceHasTray = True  # just assume
            self._deviceCanEject = True  # just assume

    #############
    # Properties
    #############

    def _getDevice(self):
        """
        Property target used to get the device value.
        """
        return self._device

    def _getScsiId(self):
        """
        Property target used to get the SCSI id value.
        """
        return self._scsiId

    def _getHardwareId(self):
        """
        Property target used to get the hardware id value.
        """
        return self._device

    def _getDriveSpeed(self):
        """
        Property target used to get the drive speed.
        """
        return self._driveSpeed

    def _getMedia(self):
        """
        Property target used to get the media description.
        """
        return self._media

    def _getDeviceHasTray(self):
        """
        Property target used to get the device-has-tray flag.
        """
        return self._deviceHasTray

    def _getDeviceCanEject(self):
        """
        Property target used to get the device-can-eject flag.
        """
        return self._deviceCanEject

    def _getRefreshMediaDelay(self):
        """
        Property target used to get the configured refresh media delay, in seconds.
        """
        return self._refreshMediaDelay

    def _getEjectDelay(self):
        """
        Property target used to get the configured eject delay, in seconds.
        """
        return self._ejectDelay

    device = property(_getDevice, None, None, doc="Filesystem device name for this writer.")
    scsiId = property(_getScsiId, None, None, doc="SCSI id for the device (saved for reference only).")
    hardwareId = property(_getHardwareId, None, None, doc="Hardware id for this writer (always the device path).")
    driveSpeed = property(_getDriveSpeed, None, None, doc="Speed at which the drive writes.")
    media = property(_getMedia, None, None, doc="Definition of media that is expected to be in the device.")
    deviceHasTray = property(_getDeviceHasTray, None, None, doc="Indicates whether the device has a media tray.")
    deviceCanEject = property(_getDeviceCanEject, None, None, doc="Indicates whether the device supports ejecting its media.")
    refreshMediaDelay = property(_getRefreshMediaDelay, None, None, doc="Refresh media delay, in seconds.")
    ejectDelay = property(_getEjectDelay, None, None, doc="Eject delay, in seconds.")

    #################################################
    # Methods related to device and media attributes
    #################################################

    def isRewritable(self):
        """Indicates whether the media is rewritable per configuration."""
        return self._media.rewritable

    def retrieveCapacity(self, entireDisc=False):
        """
        Retrieves capacity for the current media in terms of a ``MediaCapacity``
        object.

        If ``entireDisc`` is passed in as ``True``, the capacity will be for the
        entire disc, as if it were to be rewritten from scratch.  The same will
        happen if the disc can't be read for some reason. Otherwise, the capacity
        will be calculated by subtracting the sectors currently used on the disc,
        as reported by ``growisofs`` itself.

        Args:
           entireDisc (Boolean true/false): Indicates whether to return capacity for entire disc
        Returns:
            ``MediaCapacity`` object describing the capacity of the media

        Raises:
           ValueError: If there is a problem parsing the ``growisofs`` output
           IOError: If the media could not be read for some reason
        """
        sectorsUsed = 0.0
        if not entireDisc:
            sectorsUsed = self._retrieveSectorsUsed()
        sectorsAvailable = self._media.capacity - sectorsUsed  # both are in sectors
        bytesUsed = convertSize(sectorsUsed, UNIT_SECTORS, UNIT_BYTES)
        bytesAvailable = convertSize(sectorsAvailable, UNIT_SECTORS, UNIT_BYTES)
        return MediaCapacity(bytesUsed, bytesAvailable)

    #######################################################
    # Methods used for working with the internal ISO image
    #######################################################

    def initializeImage(self, newDisc, tmpdir, mediaLabel=None):
        """
        Initializes the writer's associated ISO image.

        This method initializes the ``image`` instance variable so that the caller
        can use the ``addImageEntry`` method.  Once entries have been added, the
        ``writeImage`` method can be called with no arguments.

        Args:
           newDisc (Boolean true/false): Indicates whether the disc should be re-initialized
           tmpdir (String representing a directory path on disk): Temporary directory to use if needed
           mediaLabel (String, no more than 25 characters long): Media label to be applied to the image, if any

        """
        self._image = _ImageProperties()
        self._image.newDisc = newDisc
        self._image.tmpdir = encodePath(tmpdir)
        self._image.mediaLabel = mediaLabel
        self._image.entries = {}  # mapping from path to graft point (if any)

    def addImageEntry(self, path, graftPoint):
        """
        Adds a filepath entry to the writer's associated ISO image.

        The contents of the filepath -- but not the path itself -- will be added
        to the image at the indicated graft point.  If you don't want to use a
        graft point, just pass ``None``.

        *Note:* Before calling this method, you must call :any:`initializeImage`.

        Args:
           path (String representing a path on disk): File or directory to be added to the image
           graftPoint (String representing a graft point path, as described above): Graft point to be used when adding this entry
        Raises:
           ValueError: If initializeImage() was not previously called
           ValueError: If the path is not a valid file or directory
        """
        if self._image is None:
            raise ValueError("Must call initializeImage() before using this method.")
        if not os.path.exists(path):
            raise ValueError("Path [%s] does not exist." % path)
        self._image.entries[path] = graftPoint

    def setImageNewDisc(self, newDisc):
        """
        Resets (overrides) the newDisc flag on the internal image.
        Args:
           newDisc: New disc flag to set
        Raises:
           ValueError: If initializeImage() was not previously called
        """
        if self._image is None:
            raise ValueError("Must call initializeImage() before using this method.")
        self._image.newDisc = newDisc

    def getEstimatedImageSize(self):
        """
        Gets the estimated size of the image associated with the writer.

        This is an estimate and is conservative.  The actual image could be as
        much as 450 blocks (sectors) smaller under some circmstances.

        Returns:
            Estimated size of the image, in bytes

        Raises:
           IOError: If there is a problem calling ``mkisofs``
           ValueError: If initializeImage() was not previously called
        """
        if self._image is None:
            raise ValueError("Must call initializeImage() before using this method.")
        return DvdWriter._getEstimatedImageSize(self._image.entries)

    ######################################
    # Methods which expose device actions
    ######################################

    def openTray(self):
        """
        Opens the device's tray and leaves it open.

        This only works if the device has a tray and supports ejecting its media.
        We have no way to know if the tray is currently open or closed, so we
        just send the appropriate command and hope for the best.  If the device
        does not have a tray or does not support ejecting its media, then we do
        nothing.

        Starting with Debian wheezy on my backup hardware, I started seeing
        consistent problems with the eject command.  I couldn't tell whether
        these problems were due to the device management system or to the new
        kernel (3.2.0).  Initially, I saw simple eject failures, possibly because
        I was opening and closing the tray too quickly.  I worked around that
        behavior with the new ejectDelay flag.

        Later, I sometimes ran into issues after writing an image to a disc:
        eject would give errors like "unable to eject, last error: Inappropriate
        ioctl for device".  Various sources online (like Ubuntu bug #875543)
        suggested that the drive was being locked somehow, and that the
        workaround was to run 'eject -i off' to unlock it.  Sure enough, that
        fixed the problem for me, so now it's a normal error-handling strategy.

        Raises:
           IOError: If there is an error talking to the device
        """
        if self._deviceHasTray and self._deviceCanEject:
            command = resolveCommand(EJECT_COMMAND)
            args = [self.device]
            result = executeCommand(command, args)[0]
            if result != 0:
                logger.debug("Eject failed; attempting kludge of unlocking the tray before retrying.")
                self.unlockTray()
                result = executeCommand(command, args)[0]
                if result != 0:
                    raise IOError("Error (%d) executing eject command to open tray (failed even after unlocking tray)." % result)
                logger.debug("Kludge was apparently successful.")
            if self.ejectDelay is not None:
                logger.debug("Per configuration, sleeping %d seconds after opening tray.", self.ejectDelay)
                time.sleep(self.ejectDelay)

    def unlockTray(self):
        """
        Unlocks the device's tray via 'eject -i off'.
        Raises:
           IOError: If there is an error talking to the device
        """
        command = resolveCommand(EJECT_COMMAND)
        args = ["-i", "off", self.device]
        result = executeCommand(command, args)[0]
        if result != 0:
            raise IOError("Error (%d) executing eject command to unlock tray." % result)

    def closeTray(self):
        """
        Closes the device's tray.

        This only works if the device has a tray and supports ejecting its media.
        We have no way to know if the tray is currently open or closed, so we
        just send the appropriate command and hope for the best.  If the device
        does not have a tray or does not support ejecting its media, then we do
        nothing.

        Raises:
           IOError: If there is an error talking to the device
        """
        if self._deviceHasTray and self._deviceCanEject:
            command = resolveCommand(EJECT_COMMAND)
            args = ["-t", self.device]
            result = executeCommand(command, args)[0]
            if result != 0:
                raise IOError("Error (%d) executing eject command to close tray." % result)

    def refreshMedia(self):
        """
        Opens and then immediately closes the device's tray, to refresh the
        device's idea of the media.

        Sometimes, a device gets confused about the state of its media.  Often,
        all it takes to solve the problem is to eject the media and then
        immediately reload it.  (There are also configurable eject and refresh
        media delays which can be applied, for situations where this makes a
        difference.)

        This only works if the device has a tray and supports ejecting its media.
        We have no way to know if the tray is currently open or closed, so we
        just send the appropriate command and hope for the best.  If the device
        does not have a tray or does not support ejecting its media, then we do
        nothing.  The configured delays still apply, though.

        Raises:
           IOError: If there is an error talking to the device
        """
        self.openTray()
        self.closeTray()
        self.unlockTray()  # on some systems, writing a disc leaves the tray locked, yikes!
        if self.refreshMediaDelay is not None:
            logger.debug("Per configuration, sleeping %d seconds to stabilize media state.", self.refreshMediaDelay)
            time.sleep(self.refreshMediaDelay)
        logger.debug("Media refresh complete; hopefully media state is stable now.")

    def writeImage(self, imagePath=None, newDisc=False, writeMulti=True):
        """
        Writes an ISO image to the media in the device.

        If ``newDisc`` is passed in as ``True``, we assume that the entire disc
        will be re-created from scratch.  Note that unlike ``CdWriter``,
        ``DvdWriter`` does not blank rewritable media before reusing it; however,
        ``growisofs`` is called such that the media will be re-initialized as
        needed.

        If ``imagePath`` is passed in as ``None``, then the existing image
        configured with ``initializeImage()`` will be used.  Under these
        circumstances, the passed-in ``newDisc`` flag will be ignored and the
        value passed in to ``initializeImage()`` will apply instead.

        The ``writeMulti`` argument is ignored.  It exists for compatibility with
        the Cedar Backup image writer interface.

        *Note:* The image size indicated in the log ("Image size will be...") is
        an estimate.  The estimate is conservative and is probably larger than
        the actual space that ``dvdwriter`` will use.

        Args:
           imagePath (String representing a path on disk): Path to an ISO image on disk, or ``None`` to use writer's image
           newDisc (Boolean true/false): Indicates whether the disc should be re-initialized
           writeMulti (Boolean true/false): Unused
        Raises:
           ValueError: If the image path is not absolute
           ValueError: If some path cannot be encoded properly
           IOError: If the media could not be written to for some reason
           ValueError: If no image is passed in and initializeImage() was not previously called
        """
        if not writeMulti:
            logger.warning("writeMulti value of [%s] ignored.", writeMulti)
        if imagePath is None:
            if self._image is None:
                raise ValueError("Must call initializeImage() before using this method with no image path.")
            size = self.getEstimatedImageSize()
            logger.info("Image size will be %s (estimated).", displayBytes(size))
            available = self.retrieveCapacity(entireDisc=self._image.newDisc).bytesAvailable
            if size > available:
                logger.error("Image [%s] does not fit in available capacity [%s].", displayBytes(size), displayBytes(available))
                raise IOError("Media does not contain enough capacity to store image.")
            self._writeImage(self._image.newDisc, None, self._image.entries, self._image.mediaLabel)
        else:
            if not os.path.isabs(imagePath):
                raise ValueError("Image path must be absolute.")
            imagePath = encodePath(imagePath)
            self._writeImage(newDisc, imagePath, None)

    ##################################################################
    # Utility methods for dealing with growisofs and dvd+rw-mediainfo
    ##################################################################

    def _writeImage(self, newDisc, imagePath, entries, mediaLabel=None):
        """
        Writes an image to disc using either an entries list or an ISO image on
        disk.

        Callers are assumed to have done validation on paths, etc. before calling
        this method.

        Args:
           newDisc: Indicates whether the disc should be re-initialized
           imagePath: Path to an ISO image on disk, or c{None} to use ``entries``
           entries: Mapping from path to graft point, or ``None`` to use ``imagePath``

        Raises:
           IOError: If the media could not be written to for some reason
        """
        command = resolveCommand(GROWISOFS_COMMAND)
        args = DvdWriter._buildWriteArgs(newDisc, self.hardwareId, self._driveSpeed, imagePath, entries, mediaLabel, dryRun=False)
        (result, output) = executeCommand(command, args, returnOutput=True)
        if result != 0:
            DvdWriter._searchForOverburn(output)  # throws own exception if overburn condition is found
            raise IOError("Error (%d) executing command to write disc." % result)
        self.refreshMedia()

    @staticmethod
    def _getEstimatedImageSize(entries):
        """
        Gets the estimated size of a set of image entries.

        This is implemented in terms of the ``IsoImage`` class.  The returned
        value is calculated by adding a "fudge factor" to the value from
        ``IsoImage``.  This fudge factor was determined by experimentation and is
        conservative -- the actual image could be as much as 450 blocks smaller
        under some circumstances.

        Args:
           entries: Dictionary mapping path to graft point

        Returns:
            Total estimated size of image, in bytes

        Raises:
           ValueError: If there are no entries in the dictionary
           ValueError: If any path in the dictionary does not exist
           IOError: If there is a problem calling ``mkisofs``
        """
        fudgeFactor = convertSize(2500.0, UNIT_SECTORS, UNIT_BYTES)  # determined through experimentation
        if len(list(entries.keys())) == 0:
            raise ValueError("Must add at least one entry with addImageEntry().")
        image = IsoImage()
        for path in list(entries.keys()):
            image.addEntry(path, entries[path], override=False, contentsOnly=True)
        estimatedSize = image.getEstimatedSize() + fudgeFactor
        return estimatedSize

    def _retrieveSectorsUsed(self):
        """
        Retrieves the number of sectors used on the current media.

        This is a little ugly.  We need to call growisofs in "dry-run" mode and
        parse some information from its output.  However, to do that, we need to
        create a dummy file that we can pass to the command -- and we have to
        make sure to remove it later.

        Once growisofs has been run, then we call ``_parseSectorsUsed`` to parse
        the output and calculate the number of sectors used on the media.

        Returns:
            Number of sectors used on the media
        """
        tempdir = tempfile.mkdtemp()
        try:
            entries = {tempdir: None}
            args = DvdWriter._buildWriteArgs(False, self.hardwareId, self.driveSpeed, None, entries, None, dryRun=True)
            command = resolveCommand(GROWISOFS_COMMAND)
            (result, output) = executeCommand(command, args, returnOutput=True)
            if result != 0:
                logger.debug("Error (%d) calling growisofs to read sectors used.", result)
                logger.warning("Unable to read disc (might not be initialized); returning zero sectors used.")
                return 0.0
            sectorsUsed = DvdWriter._parseSectorsUsed(output)
            logger.debug("Determined sectors used as %s", sectorsUsed)
            return sectorsUsed
        finally:
            if os.path.exists(tempdir):
                try:
                    os.rmdir(tempdir)
                except:
                    pass

    @staticmethod
    def _parseSectorsUsed(output):
        """
        Parse sectors used information out of ``growisofs`` output.

        The first line of a growisofs run looks something like this::

           Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'

        Dmitry has determined that the seek value in this line gives us
        information about how much data has previously been written to the media.
        That value multiplied by 16 yields the number of sectors used.

        If the seek line cannot be found in the output, then sectors used of zero
        is assumed.

        Returns:
            Sectors used on the media, as a floating point number

        Raises:
           ValueError: If the output cannot be parsed properly
        """
        if output is not None:
            pattern = re.compile(r"(^)(.*)(seek=)(.*)('$)")
            for line in output:
                match = pattern.search(line)
                if match is not None:
                    try:
                        return float(match.group(4).strip()) * 16.0
                    except ValueError:
                        raise ValueError("Unable to parse sectors used out of growisofs output.")
        logger.warning("Unable to read disc (might not be initialized); returning zero sectors used.")
        return 0.0

    @staticmethod
    def _searchForOverburn(output):
        """
        Search for an "overburn" error message in ``growisofs`` output.

        The ``growisofs`` command returns a non-zero exit code and puts a message
        into the output -- even on a dry run -- if there is not enough space on
        the media.  This is called an "overburn" condition.

        The error message looks like this::

           :-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!

        This method looks for the overburn error message anywhere in the output.
        If a matching error message is found, an ``IOError`` exception is raised
        containing relevant information about the problem.  Otherwise, the method
        call returns normally.

        Args:
           output: List of output lines to search, as from ``executeCommand``

        Raises:
           IOError: If an overburn condition is found
        """
        if output is None:
            return
        pattern = re.compile(r"(^)(:-[(])(\s*.*:\s*)(.* )(blocks are free, )(.* )(to be written!)")
        for line in output:
            match = pattern.search(line)
            if match is not None:
                try:
                    available = convertSize(float(match.group(4).strip()), UNIT_SECTORS, UNIT_BYTES)
                    size = convertSize(float(match.group(6).strip()), UNIT_SECTORS, UNIT_BYTES)
                    logger.error("Image [%s] does not fit in available capacity [%s].", displayBytes(size), displayBytes(available))
                except ValueError:
                    logger.error("Image does not fit in available capacity (no useful capacity info available).")
                raise IOError("Media does not contain enough capacity to store image.")

    @staticmethod
    def _buildWriteArgs(newDisc, hardwareId, driveSpeed, imagePath, entries, mediaLabel=None, dryRun=False):
        """
        Builds a list of arguments to be passed to a ``growisofs`` command.

        The arguments will either cause ``growisofs`` to write the indicated image
        file to disc, or will pass ``growisofs`` a list of directories or files
        that should be written to disc.

        If a new image is created, it will always be created with Rock Ridge
        extensions (-r).  A volume name will be applied (-V) if ``mediaLabel`` is
        not ``None``.

        Args:
           newDisc: Indicates whether the disc should be re-initialized
           hardwareId: Hardware id for the device
           driveSpeed: Speed at which the drive writes
           imagePath: Path to an ISO image on disk, or c{None} to use ``entries``
           entries: Mapping from path to graft point, or ``None`` to use ``imagePath``
           mediaLabel: Media label to set on the image, if any
           dryRun: Says whether to make this a dry run (for checking capacity)

        *Note:* If we write an existing image to disc, then the mediaLabel is
        ignored.  The media label is an attribute of the image, and should be set
        on the image when it is created.

        *Note:* We always pass the undocumented option ``-use-the-force-like=tty``
        to growisofs.  Without this option, growisofs will refuse to execute
        certain actions when running from cron.  A good example is -Z, which
        happily overwrites an existing DVD from the command-line, but fails when
        run from cron.  It took a while to figure that out, since it worked every
        time I tested it by hand. :(

        Returns:
            List suitable for passing to :any:`util.executeCommand` as ``args``

        Raises:
           ValueError: If caller does not pass one or the other of imagePath or entries
        """
        args = []
        if (imagePath is None and entries is None) or (imagePath is not None and entries is not None):
            raise ValueError("Must use either imagePath or entries.")
        args.append("-use-the-force-luke=tty")  # tell growisofs to let us run from cron
        if dryRun:
            args.append("-dry-run")
        if driveSpeed is not None:
            args.append("-speed=%d" % driveSpeed)
        if newDisc:
            args.append("-Z")
        else:
            args.append("-M")
        if imagePath is not None:
            args.append("%s=%s" % (hardwareId, imagePath))
        else:
            args.append(hardwareId)
            if mediaLabel is not None:
                args.append("-V")
                args.append(mediaLabel)
            args.append("-r")  # Rock Ridge extensions with sane ownership and permissions
            args.append("-graft-points")
            keys = list(entries.keys())
            keys.sort()  # just so we get consistent results
            for key in keys:
                # Same syntax as when calling mkisofs in IsoImage
                if entries[key] is None:
                    args.append(key)
                else:
                    args.append("%s/=%s" % (entries[key].strip("/"), key))
        return args
