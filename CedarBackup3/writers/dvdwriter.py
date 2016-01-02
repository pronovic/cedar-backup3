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
# Language : Python 3 (>= 3.4)
# Project  : Cedar Backup, release 3
# Purpose  : Provides functionality related to DVD writer devices.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides functionality related to DVD writer devices.

@sort: MediaDefinition, DvdWriter, MEDIA_DVDPLUSR, MEDIA_DVDPLUSRW

@var MEDIA_DVDPLUSR: Constant representing DVD+R media.
@var MEDIA_DVDPLUSRW: Constant representing DVD+RW media.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
@author: Dmitry Rutsky <rutsky@inbox.ru>
"""

########################################################################
# Imported modules
########################################################################

# System modules
import os
import re
import logging
import tempfile
import time

# Cedar Backup modules
from CedarBackup3.writers.util import IsoImage
from CedarBackup3.util import resolveCommand, executeCommand
from CedarBackup3.util import convertSize, displayBytes, encodePath
from CedarBackup3.util import UNIT_SECTORS, UNIT_BYTES, UNIT_GBYTES
from CedarBackup3.writers.util import validateDevice, validateDriveSpeed


########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.writers.dvdwriter")

MEDIA_DVDPLUSR  = 1
MEDIA_DVDPLUSRW = 2

GROWISOFS_COMMAND = [ "growisofs", ]
EJECT_COMMAND     = [ "eject", ]


########################################################################
# MediaDefinition class definition
########################################################################

class MediaDefinition(object):

   """
   Class encapsulating information about DVD media definitions.

   The following media types are accepted:

         - C{MEDIA_DVDPLUSR}: DVD+R media (4.4 GB capacity)
         - C{MEDIA_DVDPLUSRW}: DVD+RW media (4.4 GB capacity)

   Note that the capacity attribute returns capacity in terms of ISO sectors
   (C{util.ISO_SECTOR_SIZE)}.  This is for compatibility with the CD writer
   functionality.

   The capacities are 4.4 GB because Cedar Backup deals in "true" gigabytes
   of 1024*1024*1024 bytes per gigabyte.

   @sort: __init__, mediaType, rewritable, capacity
   """

   def __init__(self, mediaType):
      """
      Creates a media definition for the indicated media type.
      @param mediaType: Type of the media, as discussed above.
      @raise ValueError: If the media type is unknown or unsupported.
      """
      self._mediaType = None
      self._rewritable = False
      self._capacity = 0.0
      self._setValues(mediaType)

   def _setValues(self, mediaType):
      """
      Sets values based on media type.
      @param mediaType: Type of the media, as discussed above.
      @raise ValueError: If the media type is unknown or unsupported.
      """
      if mediaType not in [MEDIA_DVDPLUSR, MEDIA_DVDPLUSRW, ]:
         raise ValueError("Invalid media type %d." % mediaType)
      self._mediaType = mediaType
      if self._mediaType == MEDIA_DVDPLUSR:
         self._rewritable = False
         self._capacity = convertSize(4.4, UNIT_GBYTES, UNIT_SECTORS)   # 4.4 "true" GB = 4.7 "marketing" GB
      elif self._mediaType == MEDIA_DVDPLUSRW:
         self._rewritable = True
         self._capacity = convertSize(4.4, UNIT_GBYTES, UNIT_SECTORS)   # 4.4 "true" GB = 4.7 "marketing" GB

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

   @sort: __init__, bytesUsed, bytesAvailable, totalCapacity, utilized
   """

   def __init__(self, bytesUsed, bytesAvailable):
      """
      Initializes a capacity object.
      @raise ValueError: If the bytes used and available values are not floats.
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
   Simple value object to hold image properties for C{DvdWriter}.
   """
   def __init__(self):
      self.newDisc = False
      self.tmpdir = None
      self.mediaLabel = None
      self.entries = None     # dict mapping path to graft point


########################################################################
# DvdWriter class definition
########################################################################

class DvdWriter(object):

   ######################
   # Class documentation
   ######################

   """
   Class representing a device that knows how to write some kinds of DVD media.

   Summary
   =======

      This is a class representing a device that knows how to write some kinds
      of DVD media.  It provides common operations for the device, such as
      ejecting the media and writing data to the media.

      This class is implemented in terms of the C{eject} and C{growisofs}
      utilities, all of which should be available on most UN*X platforms.

   Image Writer Interface
   ======================

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

      Unlike the C{CdWriter}, the C{DvdWriter} can only operate in terms of
      filesystem devices, not SCSI devices.  So, although the constructor
      interface accepts a SCSI device parameter for the sake of compatibility,
      it's not used.

   Media Types
   ===========

      This class knows how to write to DVD+R and DVD+RW media, represented
      by the following constants:

         - C{MEDIA_DVDPLUSR}: DVD+R media (4.4 GB capacity)
         - C{MEDIA_DVDPLUSRW}: DVD+RW media (4.4 GB capacity)

      The difference is that DVD+RW media can be rewritten, while DVD+R media
      cannot be (although at present, C{DvdWriter} does not really
      differentiate between rewritable and non-rewritable media).

      The capacities are 4.4 GB because Cedar Backup deals in "true" gigabytes
      of 1024*1024*1024 bytes per gigabyte.

      The underlying C{growisofs} utility does support other kinds of media
      (including DVD-R, DVD-RW and BlueRay) which work somewhat differently
      than standard DVD+R and DVD+RW media.  I don't support these other kinds
      of media because I haven't had any opportunity to work with them.  The
      same goes for dual-layer media of any type.

   Device Attributes vs. Media Attributes
   ======================================

      As with the cdwriter functionality, a given dvdwriter instance has two
      different kinds of attributes associated with it.  I call these device
      attributes and media attributes.

      Device attributes are things which can be determined without looking at
      the media.  Media attributes are attributes which vary depending on the
      state of the media.  In general, device attributes are available via
      instance variables and are constant over the life of an object, while
      media attributes can be retrieved through method calls.

      Compared to cdwriters, dvdwriters have very few attributes.  This is due
      to differences between the way C{growisofs} works relative to
      C{cdrecord}.

   Media Capacity
   ==============

      One major difference between the C{cdrecord}/C{mkisofs} utilities used by
      the cdwriter class and the C{growisofs} utility used here is that the
      process of estimating remaining capacity and image size is more
      straightforward with C{cdrecord}/C{mkisofs} than with C{growisofs}.

      In this class, remaining capacity is calculated by asking doing a dry run
      of C{growisofs} and grabbing some information from the output of that
      command.  Image size is estimated by asking the C{IsoImage} class for an
      estimate and then adding on a "fudge factor" determined through
      experimentation.

   Testing
   =======

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

   @sort: __init__, isRewritable, retrieveCapacity, openTray, closeTray, refreshMedia,
          initializeImage, addImageEntry, writeImage, setImageNewDisc, getEstimatedImageSize,
          _writeImage, _getEstimatedImageSize, _searchForOverburn, _buildWriteArgs,
          device, scsiId, hardwareId, driveSpeed, media, deviceHasTray, deviceCanEject
   """

   ##############
   # Constructor
   ##############

   def __init__(self, device, scsiId=None, driveSpeed=None,
                mediaType=MEDIA_DVDPLUSRW, noEject=False,
                refreshMediaDelay=0, ejectDelay=0, unittest=False):
      """
      Initializes a DVD writer object.

      Since C{growisofs} can only address devices using the device path (i.e.
      C{/dev/dvd}), the hardware id will always be set based on the device.  If
      passed in, it will be saved for reference purposes only.

      We have no way to query the device to ask whether it has a tray or can be
      safely opened and closed.  So, the C{noEject} flag is used to set these
      values.  If C{noEject=False}, then we assume a tray exists and open/close
      is safe.  If C{noEject=True}, then we assume that there is no tray and
      open/close is not safe.

      @note: The C{unittest} parameter should never be set to C{True}
      outside of Cedar Backup code.  It is intended for use in unit testing
      Cedar Backup internals and has no other sensible purpose.

      @param device: Filesystem device associated with this writer.
      @type device: Absolute path to a filesystem device, i.e. C{/dev/dvd}

      @param scsiId: SCSI id for the device (optional, for reference only).
      @type scsiId: If provided, SCSI id in the form C{[<method>:]scsibus,target,lun}

      @param driveSpeed: Speed at which the drive writes.
      @type driveSpeed: Use C{2} for 2x device, etc. or C{None} to use device default.

      @param mediaType: Type of the media that is assumed to be in the drive.
      @type mediaType: One of the valid media type as discussed above.

      @param noEject: Tells Cedar Backup that the device cannot safely be ejected
      @type noEject: Boolean true/false

      @param refreshMediaDelay: Refresh media delay to use, if any
      @type refreshMediaDelay: Number of seconds, an integer >= 0

      @param ejectDelay: Eject delay to use, if any
      @type ejectDelay: Number of seconds, an integer >= 0

      @param unittest: Turns off certain validations, for use in unit testing.
      @type unittest: Boolean true/false

      @raise ValueError: If the device is not valid for some reason.
      @raise ValueError: If the SCSI id is not in a valid form.
      @raise ValueError: If the drive speed is not an integer >= 1.
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
         self._deviceHasTray = True   # just assume
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
      Retrieves capacity for the current media in terms of a C{MediaCapacity}
      object.

      If C{entireDisc} is passed in as C{True}, the capacity will be for the
      entire disc, as if it were to be rewritten from scratch.  The same will
      happen if the disc can't be read for some reason. Otherwise, the capacity
      will be calculated by subtracting the sectors currently used on the disc,
      as reported by C{growisofs} itself.

      @param entireDisc: Indicates whether to return capacity for entire disc.
      @type entireDisc: Boolean true/false

      @return: C{MediaCapacity} object describing the capacity of the media.

      @raise ValueError: If there is a problem parsing the C{growisofs} output
      @raise IOError: If the media could not be read for some reason.
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

      This method initializes the C{image} instance variable so that the caller
      can use the C{addImageEntry} method.  Once entries have been added, the
      C{writeImage} method can be called with no arguments.

      @param newDisc: Indicates whether the disc should be re-initialized
      @type newDisc: Boolean true/false

      @param tmpdir: Temporary directory to use if needed
      @type tmpdir: String representing a directory path on disk

      @param mediaLabel: Media label to be applied to the image, if any
      @type mediaLabel: String, no more than 25 characters long
      """
      self._image = _ImageProperties()
      self._image.newDisc = newDisc
      self._image.tmpdir = encodePath(tmpdir)
      self._image.mediaLabel = mediaLabel
      self._image.entries = {} # mapping from path to graft point (if any)

   def addImageEntry(self, path, graftPoint):
      """
      Adds a filepath entry to the writer's associated ISO image.

      The contents of the filepath -- but not the path itself -- will be added
      to the image at the indicated graft point.  If you don't want to use a
      graft point, just pass C{None}.

      @note: Before calling this method, you must call L{initializeImage}.

      @param path: File or directory to be added to the image
      @type path: String representing a path on disk

      @param graftPoint: Graft point to be used when adding this entry
      @type graftPoint: String representing a graft point path, as described above

      @raise ValueError: If initializeImage() was not previously called
      @raise ValueError: If the path is not a valid file or directory
      """
      if self._image is None:
         raise ValueError("Must call initializeImage() before using this method.")
      if not os.path.exists(path):
         raise ValueError("Path [%s] does not exist." % path)
      self._image.entries[path] = graftPoint

   def setImageNewDisc(self, newDisc):
      """
      Resets (overrides) the newDisc flag on the internal image.
      @param newDisc: New disc flag to set
      @raise ValueError: If initializeImage() was not previously called
      """
      if self._image is None:
         raise ValueError("Must call initializeImage() before using this method.")
      self._image.newDisc = newDisc

   def getEstimatedImageSize(self):
      """
      Gets the estimated size of the image associated with the writer.

      This is an estimate and is conservative.  The actual image could be as
      much as 450 blocks (sectors) smaller under some circmstances.

      @return: Estimated size of the image, in bytes.

      @raise IOError: If there is a problem calling C{mkisofs}.
      @raise ValueError: If initializeImage() was not previously called
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

      @raise IOError: If there is an error talking to the device.
      """
      if self._deviceHasTray and self._deviceCanEject:
         command = resolveCommand(EJECT_COMMAND)
         args = [ self.device, ]
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
      @raise IOError: If there is an error talking to the device.
      """
      command = resolveCommand(EJECT_COMMAND)
      args = [ "-i", "off", self.device, ]
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

      @raise IOError: If there is an error talking to the device.
      """
      if self._deviceHasTray and self._deviceCanEject:
         command = resolveCommand(EJECT_COMMAND)
         args = [ "-t", self.device, ]
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

      @raise IOError: If there is an error talking to the device.
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

      If C{newDisc} is passed in as C{True}, we assume that the entire disc
      will be re-created from scratch.  Note that unlike C{CdWriter},
      C{DvdWriter} does not blank rewritable media before reusing it; however,
      C{growisofs} is called such that the media will be re-initialized as
      needed.

      If C{imagePath} is passed in as C{None}, then the existing image
      configured with C{initializeImage()} will be used.  Under these
      circumstances, the passed-in C{newDisc} flag will be ignored and the
      value passed in to C{initializeImage()} will apply instead.

      The C{writeMulti} argument is ignored.  It exists for compatibility with
      the Cedar Backup image writer interface.

      @note: The image size indicated in the log ("Image size will be...") is
      an estimate.  The estimate is conservative and is probably larger than
      the actual space that C{dvdwriter} will use.

      @param imagePath: Path to an ISO image on disk, or C{None} to use writer's image
      @type imagePath: String representing a path on disk

      @param newDisc: Indicates whether the disc should be re-initialized
      @type newDisc: Boolean true/false.

      @param writeMulti: Unused
      @type writeMulti: Boolean true/false

      @raise ValueError: If the image path is not absolute.
      @raise ValueError: If some path cannot be encoded properly.
      @raise IOError: If the media could not be written to for some reason.
      @raise ValueError: If no image is passed in and initializeImage() was not previously called
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

      @param newDisc: Indicates whether the disc should be re-initialized
      @param imagePath: Path to an ISO image on disk, or c{None} to use C{entries}
      @param entries: Mapping from path to graft point, or C{None} to use C{imagePath}

      @raise IOError: If the media could not be written to for some reason.
      """
      command = resolveCommand(GROWISOFS_COMMAND)
      args = DvdWriter._buildWriteArgs(newDisc, self.hardwareId, self._driveSpeed, imagePath, entries, mediaLabel, dryRun=False)
      (result, output) = executeCommand(command, args, returnOutput=True)
      if result != 0:
         DvdWriter._searchForOverburn(output) # throws own exception if overburn condition is found
         raise IOError("Error (%d) executing command to write disc." % result)
      self.refreshMedia()

   @staticmethod
   def _getEstimatedImageSize(entries):
      """
      Gets the estimated size of a set of image entries.

      This is implemented in terms of the C{IsoImage} class.  The returned
      value is calculated by adding a "fudge factor" to the value from
      C{IsoImage}.  This fudge factor was determined by experimentation and is
      conservative -- the actual image could be as much as 450 blocks smaller
      under some circumstances.

      @param entries: Dictionary mapping path to graft point.

      @return: Total estimated size of image, in bytes.

      @raise ValueError: If there are no entries in the dictionary
      @raise ValueError: If any path in the dictionary does not exist
      @raise IOError: If there is a problem calling C{mkisofs}.
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

      Once growisofs has been run, then we call C{_parseSectorsUsed} to parse
      the output and calculate the number of sectors used on the media.

      @return: Number of sectors used on the media
      """
      tempdir = tempfile.mkdtemp()
      try:
         entries = { tempdir: None }
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
            except: pass

   @staticmethod
   def _parseSectorsUsed(output):
      """
      Parse sectors used information out of C{growisofs} output.

      The first line of a growisofs run looks something like this::

         Executing 'mkisofs -C 973744,1401056 -M /dev/fd/3 -r -graft-points music4/=music | builtin_dd of=/dev/cdrom obs=32k seek=87566'

      Dmitry has determined that the seek value in this line gives us
      information about how much data has previously been written to the media.
      That value multiplied by 16 yields the number of sectors used.

      If the seek line cannot be found in the output, then sectors used of zero
      is assumed.

      @return: Sectors used on the media, as a floating point number.

      @raise ValueError: If the output cannot be parsed properly.
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
      Search for an "overburn" error message in C{growisofs} output.

      The C{growisofs} command returns a non-zero exit code and puts a message
      into the output -- even on a dry run -- if there is not enough space on
      the media.  This is called an "overburn" condition.

      The error message looks like this::

         :-( /dev/cdrom: 894048 blocks are free, 2033746 to be written!

      This method looks for the overburn error message anywhere in the output.
      If a matching error message is found, an C{IOError} exception is raised
      containing relevant information about the problem.  Otherwise, the method
      call returns normally.

      @param output: List of output lines to search, as from C{executeCommand}

      @raise IOError: If an overburn condition is found.
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
      Builds a list of arguments to be passed to a C{growisofs} command.

      The arguments will either cause C{growisofs} to write the indicated image
      file to disc, or will pass C{growisofs} a list of directories or files
      that should be written to disc.

      If a new image is created, it will always be created with Rock Ridge
      extensions (-r).  A volume name will be applied (-V) if C{mediaLabel} is
      not C{None}.

      @param newDisc: Indicates whether the disc should be re-initialized
      @param hardwareId: Hardware id for the device
      @param driveSpeed: Speed at which the drive writes.
      @param imagePath: Path to an ISO image on disk, or c{None} to use C{entries}
      @param entries: Mapping from path to graft point, or C{None} to use C{imagePath}
      @param mediaLabel: Media label to set on the image, if any
      @param dryRun: Says whether to make this a dry run (for checking capacity)

      @note: If we write an existing image to disc, then the mediaLabel is
      ignored.  The media label is an attribute of the image, and should be set
      on the image when it is created.

      @note: We always pass the undocumented option C{-use-the-force-like=tty}
      to growisofs.  Without this option, growisofs will refuse to execute
      certain actions when running from cron.  A good example is -Z, which
      happily overwrites an existing DVD from the command-line, but fails when
      run from cron.  It took a while to figure that out, since it worked every
      time I tested it by hand. :(

      @return: List suitable for passing to L{util.executeCommand} as C{args}.

      @raise ValueError: If caller does not pass one or the other of imagePath or entries.
      """
      args = []
      if (imagePath is None and entries is None) or (imagePath is not None and entries is not None):
         raise ValueError("Must use either imagePath or entries.")
      args.append("-use-the-force-luke=tty") # tell growisofs to let us run from cron
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
         args.append("-r")    # Rock Ridge extensions with sane ownership and permissions
         args.append("-graft-points")
         keys = list(entries.keys())
         keys.sort() # just so we get consistent results
         for key in keys:
            # Same syntax as when calling mkisofs in IsoImage
            if entries[key] is None:
               args.append(key)
            else:
               args.append("%s/=%s" % (entries[key].strip("/"), key))
      return args

