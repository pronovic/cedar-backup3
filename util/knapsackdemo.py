#!/usr/bin/env python
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
# Copyright (c) 2004-2005,2010 Kenneth J. Pronovici.
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
# Revision : $Id: knapsackdemo.py 1006 2010-07-07 21:03:57Z pronovic $
# Purpose  : Demo the knapsack functionality in knapsack.py
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Notes
########################################################################

"""
Demo the knapsack functionality in knapsack.py.

This is a little test program that shows how the various knapsack algorithms
work.  Use 'python knapsackdemo.py' to run the program.  The usage is::

    Usage: knapsackdemo.py dir capacity
    Tests various knapsack (fit) algorithms on dir, using
    capacity (in MB) as the target fill point.

You'll get a good feel for how it works using something like this::

    python knapsackdemo.py /usr/bin 35

The output should look fine on an 80-column display.  On my Duron 850 with
784MB of RAM (Linux 2.6, Python 2.3), this runs in 0.360 seconds of elapsed
time (neglecting the time required to build the list of files to fit).  A
bigger, nastier test is to build a 650 MB list out of / or /usr.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules and constants
########################################################################

import sys
import os
import time
from CedarBackup2.filesystem import BackupFileList
from CedarBackup2.knapsack import firstFit, bestFit, worstFit, alternateFit

BYTES_PER_KBYTE = 1024.0
KBYTES_PER_MBYTE = 1024.0
BYTES_PER_MBYTE = BYTES_PER_KBYTE * KBYTES_PER_MBYTE


##################
# main() function
##################

def main():

   """Main routine."""

   # Check arguments
   if len(sys.argv) != 3:
      print "Usage: %s dir capacity" % sys.argv[0]
      print "Tests various knapsack (fit) algorithms on dir, using"
      print "capacity (in MB) as the target fill point."
      sys.exit(1)

   searchDir = sys.argv[1]
   capacity = float(sys.argv[2])

   # Print a starting banner
   print ""
   print "=============================================================="
   print "KNAPSACK TEST PROGRAM"
   print "=============================================================="
   print ""
   print "This program tests various knapsack (fit) algorithms using"
   print "a list of files gathered from a directory.  The algorithms"
   print "attempt to fit the files into a finite sized \"disc\"."
   print ""
   print "Each algorithm runs on a list with the same contents, although"
   print "the actual function calls are provided with a copy of the"
   print "original list, so they may use their list destructively."
   print ""
   print "=============================================================="
   print ""

   # Get information about the search directory
   start = time.time()
   start = time.time()
   files = BackupFileList()
   files.addDirContents(searchDir)
   size = files.totalSize()
   size /= BYTES_PER_MBYTE
   end = time.time()

   # Generate a table mapping file to size as needed by the knapsack algorithms
   table = { }
   for entry in files:
      if os.path.islink(entry):
         table[entry] = (entry, 0.0)
      elif os.path.isfile(entry):
         table[entry] = (entry, float(os.stat(entry).st_size))

   # Print some status information about what we're doing
   print "Note: desired capacity is %.2f MB." % capacity
   print "The search path, %s, contains about %.2f MB in %d files." % (searchDir, size, len(files))
   print "Gathering this information took about %.3f seconds." % (end - start)
   print ""

   # Define the list of tests 
   # (These are function pointers, essentially.)
   tests = { 'FIRST FIT': firstFit,
             ' BEST FIT': bestFit,
             'WORST FIT': worstFit,
             '  ALT FIT': alternateFit } 

   # Run each test
   totalElapsed = 0.0
   for key in tests.keys():

      # Run and time the test
      start = time.time()
      (items, used) = tests[key](table.copy(), capacity*BYTES_PER_MBYTE)
      end = time.time()
      count = len(items)

      # Calculate derived values
      countPercent = (float(count)/float(len(files))) * 100.0
      usedPercent = (float(used)/(float(capacity)*BYTES_PER_MBYTE)) * 100.0
      elapsed = end - start
      totalElapsed += elapsed

      # Display the results
      print "%s: %5d files (%6.2f%%), %6.2f MB (%6.2f%%), elapsed: %8.5f sec" % (
            key,
            count, countPercent,
            used/BYTES_PER_MBYTE, usedPercent,
            elapsed)

   # And, print the total elapsed time
   print "\nTotal elapsed processing time was about %.3f seconds." % totalElapsed


########################################################################
# Module entry point
########################################################################

# Run the main routine if the module is executed rather than sourced
if __name__ == '__main__':
   main()

