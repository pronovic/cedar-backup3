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
# Purpose  : Provides utilities related to image writers.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides utilities related to image writers.
:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import logging
import os
import re

from CedarBackup3.util import UNIT_BYTES, UNIT_SECTORS, convertSize, encodePath, executeCommand, pathJoin, resolveCommand

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.writers.util")

MKISOFS_COMMAND = ["mkisofs"]
VOLNAME_COMMAND = ["volname"]


########################################################################
# Functions used to portably validate certain kinds of values
########################################################################

############################
# validateDevice() function
############################


def validateDevice(device, unittest=False):
    """
    Validates a configured device.
    The device must be an absolute path, must exist, and must be writable.
    The unittest flag turns off validation of the device on disk.
    Args:
       device: Filesystem device path
       unittest: Indicates whether we're unit testing
    Returns:
        Device as a string, for instance ``"/dev/cdrw"``
    Raises:
       ValueError: If the device value is invalid
       ValueError: If some path cannot be encoded properly
    """
    if device is None:
        raise ValueError("Device must be filled in.")
    device = encodePath(device)
    if not os.path.isabs(device):
        raise ValueError("Backup device must be an absolute path.")
    if not unittest and not os.path.exists(device):
        raise ValueError("Backup device must exist on disk.")
    if not unittest and not os.access(device, os.W_OK):
        raise ValueError("Backup device is not writable by the current user.")
    return device


############################
# validateScsiId() function
############################


def validateScsiId(scsiId):
    """
    Validates a SCSI id string.
    SCSI id must be a string in the form ``[<method>:]scsibus,target,lun``.
    For Mac OS X (Darwin), we also accept the form ``IO.*Services[/N]``.
    *Note:* For consistency, if ``None`` is passed in, ``None`` will be returned.
    Args:
       scsiId: SCSI id for the device
    Returns:
        SCSI id as a string, for instance ``"ATA:1,0,0"``
    Raises:
       ValueError: If the SCSI id string is invalid
    """
    if scsiId is not None:
        pattern = re.compile(r"^\s*(.*:)?\s*[0-9][0-9]*\s*,\s*[0-9][0-9]*\s*,\s*[0-9][0-9]*\s*$")
        if not pattern.search(scsiId):
            pattern = re.compile(r"^\s*IO.*Services(/[0-9][0-9]*)?\s*$")
            if not pattern.search(scsiId):
                raise ValueError("SCSI id is not in a valid form.")
    return scsiId


################################
# validateDriveSpeed() function
################################


def validateDriveSpeed(driveSpeed):
    """
    Validates a drive speed value.
    Drive speed must be an integer which is >= 1.
    *Note:* For consistency, if ``None`` is passed in, ``None`` will be returned.
    Args:
       driveSpeed: Speed at which the drive writes
    Returns:
        Drive speed as an integer
    Raises:
       ValueError: If the drive speed value is invalid
    """
    if driveSpeed is None:
        return None
    try:
        intSpeed = int(driveSpeed)
    except TypeError:
        raise ValueError("Drive speed must be an integer >= 1.")
    if intSpeed < 1:
        raise ValueError("Drive speed must an integer >= 1.")
    return intSpeed


########################################################################
# General writer-related utility functions
########################################################################

############################
# readMediaLabel() function
############################


def readMediaLabel(devicePath):
    """
    Reads the media label (volume name) from the indicated device.
    The volume name is read using the ``volname`` command.
    Args:
       devicePath: Device path to read from
    Returns:
        Media label as a string, or None if there is no name or it could not be read
    """
    args = [devicePath]
    command = resolveCommand(VOLNAME_COMMAND)
    (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
    if result != 0:
        return None
    if output is None or len(output) < 1:
        return None
    return output[0].rstrip()


########################################################################
# IsoImage class definition
########################################################################


class IsoImage(object):

    ######################
    # Class documentation
    ######################

    """
    Represents an ISO filesystem image.

    **Summary**

    This object represents an ISO 9660 filesystem image.  It is implemented
    in terms of the ``mkisofs`` program, which has been ported to many
    operating systems and platforms.  A "sensible subset" of the ``mkisofs``
    functionality is made available through the public interface, allowing
    callers to set a variety of basic options such as publisher id,
    application id, etc. as well as specify exactly which files and
    directories they want included in their image.

    By default, the image is created using the Rock Ridge protocol (using the
    ``-r`` option to ``mkisofs``) because Rock Ridge discs are generally more
    useful on UN*X filesystems than standard ISO 9660 images.  However,
    callers can fall back to the default ``mkisofs`` functionality by setting
    the ``useRockRidge`` instance variable to ``False``.  Note, however, that
    this option is not well-tested.

    **Where Files and Directories are Placed in the Image**

    Although this class is implemented in terms of the ``mkisofs`` program,
    its standard "image contents" semantics are slightly different than the original
    ``mkisofs`` semantics.  The difference is that files and directories are
    added to the image with some additional information about their source
    directory kept intact.

    As an example, suppose you add the file ``/etc/profile`` to your image and
    you do not configure a graft point.  The file ``/profile`` will be created
    in the image.  The behavior for directories is similar.  For instance,
    suppose that you add ``/etc/X11`` to the image and do not configure a
    graft point.  In this case, the directory ``/X11`` will be created in the
    image, even if the original ``/etc/X11`` directory is empty.  I{This
    behavior differs from the standard ``mkisofs`` behavior!}

    If a graft point is configured, it will be used to modify the point at
    which a file or directory is added into an image.  Using the examples
    from above, let's assume you set a graft point of ``base`` when adding
    ``/etc/profile`` and ``/etc/X11`` to your image.  In this case, the file
    ``/base/profile`` and the directory ``/base/X11`` would be added to the
    image.

    I feel that this behavior is more consistent than the original ``mkisofs``
    behavior.  However, to be fair, it is not quite as flexible, and some
    users might not like it.  For this reason, the ``contentsOnly`` parameter
    to the :any:`addEntry` method can be used to revert to the original behavior
    if desired.

    """

    ##############
    # Constructor
    ##############

    def __init__(self, device=None, boundaries=None, graftPoint=None):
        """
        Initializes an empty ISO image object.

        Only the most commonly-used configuration items can be set using this
        constructor.  If you have a need to change the others, do so immediately
        after creating your object.

        The device and boundaries values are both required in order to write
        multisession discs.  If either is missing or ``None``, a multisession disc
        will not be written.  The boundaries tuple is in terms of ISO sectors, as
        built by an image writer class and returned in a ``writer.MediaCapacity``
        object.

        The boundaries parameter is a tuple of ``(last_sess_start, next_sess_start)``,
        as returned from ``cdrecord -msinfo``.

        Args:
           device (Either be a filesystem path or a SCSI address): Name of the device that the image will be written to
           boundaries: Session boundaries as required by ``mkisofs``, or ``None``
           graftPoint (String representing a graft point path (see :any:`addEntry`)): Default graft point for this page
        """
        self._device = None
        self._boundaries = None
        self._graftPoint = None
        self._useRockRidge = True
        self._applicationId = None
        self._biblioFile = None
        self._publisherId = None
        self._preparerId = None
        self._volumeId = None
        self.entries = {}
        self.device = device
        self.boundaries = boundaries
        self.graftPoint = graftPoint
        self.useRockRidge = True
        self.applicationId = None
        self.biblioFile = None
        self.publisherId = None
        self.preparerId = None
        self.volumeId = None
        logger.debug("Created new ISO image object.")

    #############
    # Properties
    #############

    def _setDevice(self, value):
        """
        Property target used to set the device value.
        If not ``None``, the value can be either an absolute path or a SCSI id.
        Raises:
           ValueError: If the value is not valid
        """
        try:
            if value is None:
                self._device = None
            else:
                if os.path.isabs(value):
                    self._device = value
                else:
                    self._device = validateScsiId(value)
        except ValueError:
            raise ValueError("Device must either be an absolute path or a valid SCSI id.")

    def _getDevice(self):
        """
        Property target used to get the device value.
        """
        return self._device

    def _setBoundaries(self, value):
        """
        Property target used to set the boundaries tuple.
        If not ``None``, the value must be a tuple of two integers.
        Raises:
           ValueError: If the tuple values are not integers
           IndexError: If the tuple does not contain enough elements
        """
        if value is None:
            self._boundaries = None
        else:
            self._boundaries = (int(value[0]), int(value[1]))

    def _getBoundaries(self):
        """
        Property target used to get the boundaries value.
        """
        return self._boundaries

    def _setGraftPoint(self, value):
        """
        Property target used to set the graft point.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The graft point must be a non-empty string.")
        self._graftPoint = value

    def _getGraftPoint(self):
        """
        Property target used to get the graft point.
        """
        return self._graftPoint

    def _setUseRockRidge(self, value):
        """
        Property target used to set the use RockRidge flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._useRockRidge = True
        else:
            self._useRockRidge = False

    def _getUseRockRidge(self):
        """
        Property target used to get the use RockRidge flag.
        """
        return self._useRockRidge

    def _setApplicationId(self, value):
        """
        Property target used to set the application id.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The application id must be a non-empty string.")
        self._applicationId = value

    def _getApplicationId(self):
        """
        Property target used to get the application id.
        """
        return self._applicationId

    def _setBiblioFile(self, value):
        """
        Property target used to set the biblio file.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The biblio file must be a non-empty string.")
        self._biblioFile = value

    def _getBiblioFile(self):
        """
        Property target used to get the biblio file.
        """
        return self._biblioFile

    def _setPublisherId(self, value):
        """
        Property target used to set the publisher id.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The publisher id must be a non-empty string.")
        self._publisherId = value

    def _getPublisherId(self):
        """
        Property target used to get the publisher id.
        """
        return self._publisherId

    def _setPreparerId(self, value):
        """
        Property target used to set the preparer id.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The preparer id must be a non-empty string.")
        self._preparerId = value

    def _getPreparerId(self):
        """
        Property target used to get the preparer id.
        """
        return self._preparerId

    def _setVolumeId(self, value):
        """
        Property target used to set the volume id.
        The value must be a non-empty string if it is not ``None``.
        Raises:
           ValueError: If the value is an empty string
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The volume id must be a non-empty string.")
        self._volumeId = value

    def _getVolumeId(self):
        """
        Property target used to get the volume id.
        """
        return self._volumeId

    device = property(_getDevice, _setDevice, None, "Device that image will be written to (device path or SCSI id).")
    boundaries = property(_getBoundaries, _setBoundaries, None, "Session boundaries as required by ``mkisofs``.")
    graftPoint = property(_getGraftPoint, _setGraftPoint, None, "Default image-wide graft point (see :any:`addEntry` for details).")
    useRockRidge = property(_getUseRockRidge, _setUseRockRidge, None, "Indicates whether to use RockRidge (default is ``True``).")
    applicationId = property(
        _getApplicationId, _setApplicationId, None, "Optionally specifies the ISO header application id value."
    )
    biblioFile = property(_getBiblioFile, _setBiblioFile, None, "Optionally specifies the ISO bibliographic file name.")
    publisherId = property(_getPublisherId, _setPublisherId, None, "Optionally specifies the ISO header publisher id value.")
    preparerId = property(_getPreparerId, _setPreparerId, None, "Optionally specifies the ISO header preparer id value.")
    volumeId = property(_getVolumeId, _setVolumeId, None, "Optionally specifies the ISO header volume id value.")

    #########################
    # General public methods
    #########################

    def addEntry(self, path, graftPoint=None, override=False, contentsOnly=False):
        """
        Adds an individual file or directory into the ISO image.

        The path must exist and must be a file or a directory.  By default, the
        entry will be placed into the image at the root directory, but this
        behavior can be overridden using the ``graftPoint`` parameter or instance
        variable.

        You can use the ``contentsOnly`` behavior to revert to the "original"
        ``mkisofs`` behavior for adding directories, which is to add only the
        items within the directory, and not the directory itself.

        *Note:* Things get *odd* if you try to add a directory to an image that
        will be written to a multisession disc, and the same directory already
        exists in an earlier session on that disc.  Not all of the data gets
        written.  You really wouldn't want to do this anyway, I guess.

        *Note:* An exception will be thrown if the path has already been added to
        the image, unless the ``override`` parameter is set to ``True``.

        *Note:* The method ``graftPoints`` parameter overrides the object-wide
        instance variable.  If neither the method parameter or object-wide value
        is set, the path will be written at the image root.  The graft point
        behavior is determined by the value which is in effect I{at the time this
        method is called}, so you *must* set the object-wide value before
        calling this method for the first time, or your image may not be
        consistent.

        *Note:* You *cannot* use the local ``graftPoint`` parameter to "turn off"
        an object-wide instance variable by setting it to ``None``.  Python's
        default argument functionality buys us a lot, but it can't make this
        method psychic. :)

        Args:
           path (String representing a path on disk): File or directory to be added to the image
           graftPoint (String representing a graft point path, as described above): Graft point to be used when adding this entry
           override (Boolean true/false): Override an existing entry with the same path
           contentsOnly (Boolean true/false): Add directory contents only (standard ``mkisofs`` behavior)
        Raises:
           ValueError: If path is not a file or directory, or does not exist
           ValueError: If the path has already been added, and override is not set
           ValueError: If a path cannot be encoded properly
        """
        path = encodePath(path)
        if not override:
            if path in list(self.entries.keys()):
                raise ValueError("Path has already been added to the image.")
        if os.path.islink(path):
            raise ValueError("Path must not be a link.")
        if os.path.isdir(path):
            if graftPoint is not None:
                if contentsOnly:
                    self.entries[path] = graftPoint
                else:
                    self.entries[path] = pathJoin(graftPoint, os.path.basename(path))
            elif self.graftPoint is not None:
                if contentsOnly:
                    self.entries[path] = self.graftPoint
                else:
                    self.entries[path] = pathJoin(self.graftPoint, os.path.basename(path))
            else:
                if contentsOnly:
                    self.entries[path] = None
                else:
                    self.entries[path] = os.path.basename(path)
        elif os.path.isfile(path):
            if graftPoint is not None:
                self.entries[path] = graftPoint
            elif self.graftPoint is not None:
                self.entries[path] = self.graftPoint
            else:
                self.entries[path] = None
        else:
            raise ValueError("Path must be a file or a directory.")

    def getEstimatedSize(self):
        """
        Returns the estimated size (in bytes) of the ISO image.

        This is implemented via the ``-print-size`` option to ``mkisofs``, so it
        might take a bit of time to execute.  However, the result is as accurate
        as we can get, since it takes into account all of the ISO overhead, the
        true cost of directories in the structure, etc, etc.

        Returns:
            Estimated size of the image, in bytes

        Raises:
           IOError: If there is a problem calling ``mkisofs``
           ValueError: If there are no filesystem entries in the image
        """
        if len(list(self.entries.keys())) == 0:
            raise ValueError("Image does not contain any entries.")
        return self._getEstimatedSize(self.entries)

    def _getEstimatedSize(self, entries):
        """
        Returns the estimated size (in bytes) for the passed-in entries dictionary.
        Returns:
            Estimated size of the image, in bytes
        Raises:
           IOError: If there is a problem calling ``mkisofs``
        """
        args = self._buildSizeArgs(entries)
        command = resolveCommand(MKISOFS_COMMAND)
        (result, output) = executeCommand(command, args, returnOutput=True, ignoreStderr=True)
        if result != 0:
            raise IOError("Error (%d) executing mkisofs command to estimate size." % result)
        if len(output) != 1:
            raise IOError("Unable to parse mkisofs output.")
        try:
            sectors = float(output[0])
            size = convertSize(sectors, UNIT_SECTORS, UNIT_BYTES)
            return size
        except:
            raise IOError("Unable to parse mkisofs output.")

    def writeImage(self, imagePath):
        """
        Writes this image to disk using the image path.

        Args:
           imagePath (String representing a path on disk): Path to write image out as
        Raises:
           IOError: If there is an error writing the image to disk
           ValueError: If there are no filesystem entries in the image
           ValueError: If a path cannot be encoded properly
        """
        imagePath = encodePath(imagePath)
        if len(list(self.entries.keys())) == 0:
            raise ValueError("Image does not contain any entries.")
        args = self._buildWriteArgs(self.entries, imagePath)
        command = resolveCommand(MKISOFS_COMMAND)
        (result, output) = executeCommand(command, args, returnOutput=False)
        if result != 0:
            raise IOError("Error (%d) executing mkisofs command to build image." % result)

    #########################################
    # Methods used to build mkisofs commands
    #########################################

    @staticmethod
    def _buildDirEntries(entries):
        """
        Uses an entries dictionary to build a list of directory locations for use
        by ``mkisofs``.

        We build a list of entries that can be passed to ``mkisofs``.  Each entry is
        either raw (if no graft point was configured) or in graft-point form as
        described above (if a graft point was configured).  The dictionary keys
        are the path names, and the values are the graft points, if any.

        Args:
           entries: Dictionary of image entries (i.e. self.entries)

        Returns:
            List of directory locations for use by ``mkisofs``
        """
        dirEntries = []
        for key in list(entries.keys()):
            if entries[key] is None:
                dirEntries.append(key)
            else:
                dirEntries.append("%s/=%s" % (entries[key].strip("/"), key))
        return dirEntries

    def _buildGeneralArgs(self):
        """
        Builds a list of general arguments to be passed to a ``mkisofs`` command.

        The various instance variables (``applicationId``, etc.) are filled into
        the list of arguments if they are set.
        By default, we will build a RockRidge disc.  If you decide to change
        this, think hard about whether you know what you're doing.  This option
        is not well-tested.

        Returns:
            List suitable for passing to :any:`util.executeCommand` as ``args``
        """
        args = []
        if self.applicationId is not None:
            args.append("-A")
            args.append(self.applicationId)
        if self.biblioFile is not None:
            args.append("-biblio")
            args.append(self.biblioFile)
        if self.publisherId is not None:
            args.append("-publisher")
            args.append(self.publisherId)
        if self.preparerId is not None:
            args.append("-p")
            args.append(self.preparerId)
        if self.volumeId is not None:
            args.append("-V")
            args.append(self.volumeId)
        return args

    def _buildSizeArgs(self, entries):
        """
        Builds a list of arguments to be passed to a ``mkisofs`` command.

        The various instance variables (``applicationId``, etc.) are filled into
        the list of arguments if they are set.  The command will be built to just
        return size output (a simple count of sectors via the ``-print-size`` option),
        rather than an image file on disk.

        By default, we will build a RockRidge disc.  If you decide to change
        this, think hard about whether you know what you're doing.  This option
        is not well-tested.

        Args:
           entries: Dictionary of image entries (i.e. self.entries)

        Returns:
            List suitable for passing to :any:`util.executeCommand` as ``args``
        """
        args = self._buildGeneralArgs()
        args.append("-print-size")
        args.append("-graft-points")
        if self.useRockRidge:
            args.append("-r")
        if self.device is not None and self.boundaries is not None:
            args.append("-C")
            args.append("%d,%d" % (self.boundaries[0], self.boundaries[1]))
            args.append("-M")
            args.append(self.device)
        args.extend(self._buildDirEntries(entries))
        return args

    def _buildWriteArgs(self, entries, imagePath):
        """
        Builds a list of arguments to be passed to a ``mkisofs`` command.

        The various instance variables (``applicationId``, etc.) are filled into
        the list of arguments if they are set.  The command will be built to write
        an image to disk.

        By default, we will build a RockRidge disc.  If you decide to change
        this, think hard about whether you know what you're doing.  This option
        is not well-tested.

        Args:
           entries: Dictionary of image entries (i.e. self.entries)

           imagePath (String representing a path on disk): Path to write image out as
        Returns:
            List suitable for passing to :any:`util.executeCommand` as ``args``
        """
        args = self._buildGeneralArgs()
        args.append("-graft-points")
        if self.useRockRidge:
            args.append("-r")
        args.append("-o")
        args.append(imagePath)
        if self.device is not None and self.boundaries is not None:
            args.append("-C")
            args.append("%d,%d" % (self.boundaries[0], self.boundaries[1]))
            args.append("-M")
            args.append(self.device)
        args.extend(self._buildDirEntries(entries))
        return args
