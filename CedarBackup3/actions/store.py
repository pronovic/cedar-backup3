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
# Language : Python 3 (>= 3.4)
# Project  : Cedar Backup, release 3
# Purpose  : Implements the standard 'store' action.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Implements the standard 'store' action.
@sort: executeStore, writeImage, writeStoreIndicator, consistencyCheck
@author: Kenneth J. Pronovici <pronovic@ieee.org>
@author: Dmitry Rutsky <rutsky@inbox.ru>
"""


########################################################################
# Imported modules
########################################################################

# System modules
import sys
import os
import logging
import datetime
import tempfile

# Cedar Backup modules
from CedarBackup3.filesystem import compareContents
from CedarBackup3.util import isStartOfWeek
from CedarBackup3.util import mount, unmount, displayBytes
from CedarBackup3.actions.util import createWriter, checkMediaState, buildMediaLabel, writeIndicatorFile
from CedarBackup3.actions.constants import DIR_TIME_FORMAT, STAGE_INDICATOR, STORE_INDICATOR


########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.actions.store")


########################################################################
# Public functions
########################################################################

##########################
# executeStore() function
##########################

# pylint: disable=W0613
def executeStore(configPath, options, config):
   """
   Executes the store backup action.

   @note: The rebuild action and the store action are very similar.  The
   main difference is that while store only stores a single day's staging
   directory, the rebuild action operates on multiple staging directories.

   @note: When the store action is complete, we will write a store indicator to
   the daily staging directory we used, so it's obvious that the store action
   has completed.

   @param configPath: Path to configuration file on disk.
   @type configPath: String representing a path on disk.

   @param options: Program command-line options.
   @type options: Options object.

   @param config: Program configuration.
   @type config: Config object.

   @raise ValueError: Under many generic error conditions
   @raise IOError: If there are problems reading or writing files.
   """
   logger.debug("Executing the 'store' action.")
   if sys.platform == "darwin":
      logger.warning("Warning: the store action is not fully supported on Mac OS X.")
      logger.warning("See the Cedar Backup software manual for further information.")
   if config.options is None or config.store is None:
      raise ValueError("Store configuration is not properly filled in.")
   if config.store.checkMedia:
      checkMediaState(config.store)  # raises exception if media is not initialized
   rebuildMedia = options.full
   logger.debug("Rebuild media flag [%s]", rebuildMedia)
   todayIsStart = isStartOfWeek(config.options.startingDay)
   stagingDirs = _findCorrectDailyDir(options, config)
   writeImageBlankSafe(config, rebuildMedia, todayIsStart, config.store.blankBehavior, stagingDirs)
   if config.store.checkData:
      if sys.platform == "darwin":
         logger.warning("Warning: consistency check cannot be run successfully on Mac OS X.")
         logger.warning("See the Cedar Backup software manual for further information.")
      else:
         logger.debug("Running consistency check of media.")
         consistencyCheck(config, stagingDirs)
   writeStoreIndicator(config, stagingDirs)
   logger.info("Executed the 'store' action successfully.")


########################
# writeImage() function
########################

def writeImage(config, newDisc, stagingDirs):
   """
   Builds and writes an ISO image containing the indicated stage directories.

   The generated image will contain each of the staging directories listed in
   C{stagingDirs}.  The directories will be placed into the image at the root by
   date, so staging directory C{/opt/stage/2005/02/10} will be placed into the
   disc at C{/2005/02/10}.

   @note: This function is implemented in terms of L{writeImageBlankSafe}.  The
   C{newDisc} flag is passed in for both C{rebuildMedia} and C{todayIsStart}.

   @param config: Config object.
   @param newDisc: Indicates whether the disc should be re-initialized
   @param stagingDirs: Dictionary mapping directory path to date suffix.

   @raise ValueError: Under many generic error conditions
   @raise IOError: If there is a problem writing the image to disc.
   """
   writeImageBlankSafe(config, newDisc, newDisc, None, stagingDirs)


#################################
# writeImageBlankSafe() function
#################################

def writeImageBlankSafe(config, rebuildMedia, todayIsStart, blankBehavior, stagingDirs):
   """
   Builds and writes an ISO image containing the indicated stage directories.

   The generated image will contain each of the staging directories listed in
   C{stagingDirs}.  The directories will be placed into the image at the root by
   date, so staging directory C{/opt/stage/2005/02/10} will be placed into the
   disc at C{/2005/02/10}.  The media will always be written with a media
   label specific to Cedar Backup.

   This function is similar to L{writeImage}, but tries to implement a smarter
   blanking strategy.

   First, the media is always blanked if the C{rebuildMedia} flag is true.
   Then, if C{rebuildMedia} is false, blanking behavior and C{todayIsStart}
   come into effect::

      If no blanking behavior is specified, and it is the start of the week,
      the disc will be blanked

      If blanking behavior is specified, and either the blank mode is "daily"
      or the blank mode is "weekly" and it is the start of the week, then
      the disc will be blanked if it looks like the weekly backup will not
      fit onto the media.

      Otherwise, the disc will not be blanked

   How do we decide whether the weekly backup will fit onto the media?  That is
   what the blanking factor is used for.  The following formula is used::

      will backup fit? = (bytes available / (1 + bytes required) <= blankFactor

   The blanking factor will vary from setup to setup, and will probably
   require some experimentation to get it right.

   @param config: Config object.
   @param rebuildMedia: Indicates whether media should be rebuilt
   @param todayIsStart: Indicates whether today is the starting day of the week
   @param blankBehavior: Blank behavior from configuration, or C{None} to use default behavior
   @param stagingDirs: Dictionary mapping directory path to date suffix.

   @raise ValueError: Under many generic error conditions
   @raise IOError: If there is a problem writing the image to disc.
   """
   mediaLabel = buildMediaLabel()
   writer = createWriter(config)
   writer.initializeImage(True, config.options.workingDir, mediaLabel)  # default value for newDisc
   for stageDir in list(stagingDirs.keys()):
      logger.debug("Adding stage directory [%s].", stageDir)
      dateSuffix = stagingDirs[stageDir]
      writer.addImageEntry(stageDir, dateSuffix)
   newDisc = _getNewDisc(writer, rebuildMedia, todayIsStart, blankBehavior)
   writer.setImageNewDisc(newDisc)
   writer.writeImage()

def _getNewDisc(writer, rebuildMedia, todayIsStart, blankBehavior):
   """
   Gets a value for the newDisc flag based on blanking factor rules.

   The blanking factor rules are described above by L{writeImageBlankSafe}.

   @param writer: Previously configured image writer containing image entries
   @param rebuildMedia: Indicates whether media should be rebuilt
   @param todayIsStart: Indicates whether today is the starting day of the week
   @param blankBehavior: Blank behavior from configuration, or C{None} to use default behavior

   @return: newDisc flag to be set on writer.
   """
   newDisc = False
   if rebuildMedia:
      newDisc = True
      logger.debug("Setting new disc flag based on rebuildMedia flag.")
   else:
      if blankBehavior is None:
         logger.debug("Default media blanking behavior is in effect.")
         if todayIsStart:
            newDisc = True
            logger.debug("Setting new disc flag based on todayIsStart.")
      else:
         # note: validation says we can assume that behavior is fully filled in if it exists at all
         logger.debug("Optimized media blanking behavior is in effect based on configuration.")
         if blankBehavior.blankMode == "daily" or (blankBehavior.blankMode == "weekly" and todayIsStart):
            logger.debug("New disc flag will be set based on blank factor calculation.")
            blankFactor = float(blankBehavior.blankFactor)
            logger.debug("Configured blanking factor: %.2f", blankFactor)
            available = writer.retrieveCapacity().bytesAvailable
            logger.debug("Bytes available: %s", displayBytes(available))
            required = writer.getEstimatedImageSize()
            logger.debug("Bytes required: %s", displayBytes(required))
            ratio = available / (1.0 + required)
            logger.debug("Calculated ratio: %.2f", ratio)
            newDisc = (ratio <= blankFactor)
            logger.debug("%.2f <= %.2f ? %s", ratio, blankFactor, newDisc)
         else:
            logger.debug("No blank factor calculation is required based on configuration.")
   logger.debug("New disc flag [%s].", newDisc)
   return newDisc


#################################
# writeStoreIndicator() function
#################################

def writeStoreIndicator(config, stagingDirs):
   """
   Writes a store indicator file into staging directories.

   The store indicator is written into each of the staging directories when
   either a store or rebuild action has written the staging directory to disc.

   @param config: Config object.
   @param stagingDirs: Dictionary mapping directory path to date suffix.
   """
   for stagingDir in list(stagingDirs.keys()):
      writeIndicatorFile(stagingDir, STORE_INDICATOR,
                         config.options.backupUser,
                         config.options.backupGroup)


##############################
# consistencyCheck() function
##############################

def consistencyCheck(config, stagingDirs):
   """
   Runs a consistency check against media in the backup device.

   It seems that sometimes, it's possible to create a corrupted multisession
   disc (i.e. one that cannot be read) although no errors were encountered
   while writing the disc.  This consistency check makes sure that the data
   read from disc matches the data that was used to create the disc.

   The function mounts the device at a temporary mount point in the working
   directory, and then compares the indicated staging directories in the
   staging directory and on the media.  The comparison is done via
   functionality in C{filesystem.py}.

   If no exceptions are thrown, there were no problems with the consistency
   check.  A positive confirmation of "no problems" is also written to the log
   with C{info} priority.

   @warning: The implementation of this function is very UNIX-specific.

   @param config: Config object.
   @param stagingDirs: Dictionary mapping directory path to date suffix.

   @raise ValueError: If the two directories are not equivalent.
   @raise IOError: If there is a problem working with the media.
   """
   logger.debug("Running consistency check.")
   mountPoint = tempfile.mkdtemp(dir=config.options.workingDir)
   try:
      mount(config.store.devicePath, mountPoint, "iso9660")
      for stagingDir in list(stagingDirs.keys()):
         discDir = os.path.join(mountPoint, stagingDirs[stagingDir])
         logger.debug("Checking [%s] vs. [%s].", stagingDir, discDir)
         compareContents(stagingDir, discDir, verbose=True)
         logger.info("Consistency check completed for [%s].  No problems found.", stagingDir)
   finally:
      unmount(mountPoint, True, 5, 1)  # try 5 times, and remove mount point when done


########################################################################
# Private utility functions
########################################################################

#########################
# _findCorrectDailyDir()
#########################

def _findCorrectDailyDir(options, config):
   """
   Finds the correct daily staging directory to be written to disk.

   In Cedar Backup v1.0, we assumed that the correct staging directory matched
   the current date.  However, that has problems.  In particular, it breaks
   down if collect is on one side of midnite and stage is on the other, or if
   certain processes span midnite.

   For v2.0, I'm trying to be smarter.  I'll first check the current day.  If
   that directory is found, it's good enough.  If it's not found, I'll look for
   a valid directory from the day before or day after I{which has not yet been
   staged, according to the stage indicator file}.  The first one I find, I'll
   use.  If I use a directory other than for the current day I{and}
   C{config.store.warnMidnite} is set, a warning will be put in the log.

   There is one exception to this rule.  If the C{options.full} flag is set,
   then the special "span midnite" logic will be disabled and any existing
   store indicator will be ignored.  I did this because I think that most users
   who run C{cback3 --full store} twice in a row expect the command to generate
   two identical discs.  With the other rule in place, running that command
   twice in a row could result in an error ("no unstored directory exists") or
   could even cause a completely unexpected directory to be written to disc (if
   some previous day's contents had not yet been written).

   @note: This code is probably longer and more verbose than it needs to be,
   but at least it's straightforward.

   @param options: Options object.
   @param config: Config object.

   @return: Correct staging dir, as a dict mapping directory to date suffix.
   @raise IOError: If the staging directory cannot be found.
   """
   oneDay = datetime.timedelta(days=1)
   today = datetime.date.today()
   yesterday = today - oneDay
   tomorrow = today + oneDay
   todayDate = today.strftime(DIR_TIME_FORMAT)
   yesterdayDate = yesterday.strftime(DIR_TIME_FORMAT)
   tomorrowDate = tomorrow.strftime(DIR_TIME_FORMAT)
   todayPath = os.path.join(config.stage.targetDir, todayDate)
   yesterdayPath = os.path.join(config.stage.targetDir, yesterdayDate)
   tomorrowPath = os.path.join(config.stage.targetDir, tomorrowDate)
   todayStageInd = os.path.join(todayPath, STAGE_INDICATOR)
   yesterdayStageInd = os.path.join(yesterdayPath, STAGE_INDICATOR)
   tomorrowStageInd = os.path.join(tomorrowPath, STAGE_INDICATOR)
   todayStoreInd = os.path.join(todayPath, STORE_INDICATOR)
   yesterdayStoreInd = os.path.join(yesterdayPath, STORE_INDICATOR)
   tomorrowStoreInd = os.path.join(tomorrowPath, STORE_INDICATOR)
   if options.full:
      if os.path.isdir(todayPath) and os.path.exists(todayStageInd):
         logger.info("Store process will use current day's stage directory [%s]", todayPath)
         return { todayPath:todayDate }
      raise IOError("Unable to find staging directory to store (only tried today due to full option).")
   else:
      if os.path.isdir(todayPath) and os.path.exists(todayStageInd) and not os.path.exists(todayStoreInd):
         logger.info("Store process will use current day's stage directory [%s]", todayPath)
         return { todayPath:todayDate }
      elif os.path.isdir(yesterdayPath) and os.path.exists(yesterdayStageInd) and not os.path.exists(yesterdayStoreInd):
         logger.info("Store process will use previous day's stage directory [%s]", yesterdayPath)
         if config.store.warnMidnite:
            logger.warning("Warning: store process crossed midnite boundary to find data.")
         return { yesterdayPath:yesterdayDate }
      elif os.path.isdir(tomorrowPath) and os.path.exists(tomorrowStageInd) and not os.path.exists(tomorrowStoreInd):
         logger.info("Store process will use next day's stage directory [%s]", tomorrowPath)
         if config.store.warnMidnite:
            logger.warning("Warning: store process crossed midnite boundary to find data.")
         return { tomorrowPath:tomorrowDate }
      raise IOError("Unable to find unused staging directory to store (tried today, yesterday, tomorrow).")

