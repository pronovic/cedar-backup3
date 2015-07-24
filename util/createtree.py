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
# Revision : $Id: createtree.py 1022 2011-10-11 23:27:49Z pronovic $
# Purpose  : Create a random directory structure for testing
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Notes
########################################################################

"""
What is this Program?
=====================

   In order to adequately test Cedar Backup, I need some filesystems that are
   "real enough" to stress the code.  However, building such filesystems is
   really a pain.  This program takes some parameters and generates a directory
   tree with random contents, which I can then save off and use in my testing.


Example of Configuration
========================
   
   For configuration, this program takes a Windows-style INI file that can be
   parsed by the Python ConfigParser functionality.  The following is an
   example of a valid file.  Fields not listed below will be ignored::

      [names]
      dirprefix  = dir
      fileprefix = file
      linkprefix = link

      [sizes]
      maxdepth   = 5
      mindirs    = 0
      maxdirs    = 10
      minfiles   = 0
      maxfiles   = 50
      minsize    = 0
      maxsize    = 10000

   Here's a breakdown of the various fields:

      - B{dirprefix}  - prefix used in creating names of directories
      - B{fileprefix} - prefix used in creating names of files
      - B{linkprefix} - prefix used in creating names of soft links
      - B{maxdepth}   - Maximum depth of the created tree at any given point
      - B{mindirs}    - Minimum number of directories to create at a given level, subject to depth
      - B{maxdirs}    - Maximum number of directories to create at a given level, subject to depth
      - B{minfiles}   - Minimum number of files to create at a given level
      - B{maxfiles}   - Maximum number of files to create at a given level
      - B{minlinks}   - Minimum number of soft links to create at a given level
      - B{maxlinks}   - Maximum number of soft links to create at a given level
      - B{minsize}    - Minimum size of randomly-generated files
      - B{maxsize}    - Maximum size of randomly-generated files

   No validation is done on these values, so if you do something stupid (like
   make min greater than max or something) the results are undefined.  Also,
   formatting (i.e. generation of file names) sometimes assumes that the
   maximum values are never greater than 999, so you might want to keep that in
   mind.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import sys
import os
import string  # pylint: disable=W0402
import random
from ConfigParser import SafeConfigParser


#######################################################################
# Functions
#######################################################################

###################
# usage() function
###################

def usage():
   """
   Prints out program usage information.
   """
   print ""
   print "Usage: %s <create-dir> <config-file>" % os.path.basename(sys.argv[0])
   print ""
   print "Creates a directory tree within <create-dir> based on the"
   print "configuration within <config-file>.  The directory tree will"
   print "contain a random number of directories and files of various"
   print "sizes."
   print ""
   print "The <config-file> is a Windows-style INI file that can be"
   print "parsed by the Python ConfigParser functionality.  For an"
   print "example, see internal comments in this Python script."
   print ""


########################
# createfile() function
########################

def createfile(config, filepath):
   """
   Creates a file of a random size using configuration.

   The file will be filled with random letters, digits and newlines, and will
   always be terminated with a newline.  I got the idea for the cute
   random.choice line from c.l.p.

   The directory which contains the file must already exist.

   @param config: Program configuration
   @type config: Dictionary including at least C{'minsize'} and C{'maxsize'} keys

   @param filepath: File to create
   @type filepath: String representing path to a file on disk

   @return: Size of file that was created.
   """
   characterSet = string.letters + string.digits + "\n"
   filesize = random.randint(config['minsize'], config['maxsize'])
   fp = open(filepath, "w")
   fp.write("".join([random.choice(characterSet) for i in xrange(1, filesize)]))
   fp.write("\n")
   fp.close()
   return filesize


#####################
# filldir() function
#####################

def filldir(config, basedir, depth):
   """
   Fills in a directory based on configuration.

   The directory will be filled in with a random number of files, directories
   and soft-links based on ranges specified in configuration.   Any
   newly-created directories will be recursively filled as allowed by the
   configured maximum depth.  Soft links are always created in relative terms
   (i.e.  C{link1} -> C{file1}).

   @note: When we create file, directory and link names, we assume that the
   index of the name (i.e. the counter) doesn't exceed three digits for
   formatting the filename.  The code should degrade gracefully, however.

   @note: This function may call itself recursively.  The exit condition is met
   when the configured maximum depth has been exceeded.

   @param config: Program configuration
   @type config: Dictionary of configuration items

   @param basedir: Base directory that this method is assumed to be operating within
   @type basedir: String representing a path to a directory on disk

   @param depth: Current depth into the constructed tree, for validation
   @type depth: Integer

   @return: Total number of directory elements recursively created
   """

   # Check our recursive exit condition
   if depth > config['maxdepth']: 
      return

   # Initialize list of created items for later use with links
   itemlist = []

   # Create each of the directories, recursively filling each.
   dircount = random.randint(config['mindirs'], config['maxdirs'])
   for dirindex in range(1, dircount+1):
      dirname = os.path.join(basedir, "%s%03d" % (config['dirprefix'], dirindex))
      itemlist.append(dirname)
      os.mkdir(dirname)
      filldir(config, dirname, depth+1)
      print "Created dir  [%s]." % dirname

   # Create each of the files
   filecount = random.randint(config['minfiles'], config['maxfiles'])
   for fileindex in range(1, filecount+1):
      filename = os.path.join(basedir, "%s%03d" % (config['fileprefix'], fileindex))
      itemlist.append(filename)
      size = createfile(config, filename)
      print "Created file [%s] with size [%d] bytes." % (filename, size)

   # Create each of the links, only as many as we have things to link to
   linkcount = random.randint(config['minlinks'], config['maxlinks'])
   if linkcount >= len(itemlist):
      linkitems = itemlist
   else:
      linkitems = random.sample(itemlist, linkcount)
   linkindex = 0
   for linkitem in linkitems:
      linkindex += 1
      linkname = os.path.join(basedir, "%s%03d" % (config['linkprefix'], linkindex))
      os.symlink(os.path.basename(linkitem), linkname)
      print "Created link [%s -> %s]." % (linkname, os.path.basename(linkitem))


#########################
# parseconfig() function
#########################

def parseconfig(configfile):
   """
   Parses configuration on disk.

   See the script-wide comments for documentation on the
   format of the file.  ConfigParser exceptions will be thrown
   if the format of the file is invalid.

   @param configfile: Configuration file
   @type configfile: String representing path to file on disk
   """

   # Initialize parser
   config = {} 
   parser = SafeConfigParser()
   parser.read(configfile)

   # Parse out [names] items
   config['dirprefix'] = parser.get("names", "dirprefix")
   config['fileprefix'] = parser.get("names", "fileprefix")
   config['linkprefix'] = parser.get("names", "linkprefix")

   # Parse out [sizes] items
   config['maxdepth'] = parser.getint("sizes", "maxdepth")
   config['mindirs'] = parser.getint("sizes", "mindirs")
   config['maxdirs'] = parser.getint("sizes", "maxdirs")
   config['minfiles'] = parser.getint("sizes", "minfiles")
   config['maxfiles'] = parser.getint("sizes", "maxfiles")
   config['minlinks'] = parser.getint("sizes", "minlinks")
   config['maxlinks'] = parser.getint("sizes", "maxlinks")
   config['minsize'] = parser.getint("sizes", "minsize")
   config['maxsize'] = parser.getint("sizes", "maxsize")

   # Return the result
   return config


##################
# main() function
##################

def main():

   """
   Main routine for program.
   """

   # Handle arguments
   basedir = None
   configfile = None
   config = None

   # Parse command-line
   try:
      basedir = sys.argv[1]
      configfile = sys.argv[2]
   except Exception:
      usage()
      sys.exit(1)

   # Parse configuration   
   try:
      config = parseconfig(configfile)
   except Exception, e:
      print "Unable to parse configuration file: %s" % e
      sys.exit(2)

   # Validate the base directory
   if os.path.exists(basedir):
      print "Path [%s] already exists; aborting." % basedir
      sys.exit(2)

   # Create the tree (this is a recursive call)
   try:
      os.mkdir(basedir)
      filldir(config, basedir, 1)
   except Exception, e:
      print "Error filling directory: %s" % e

   # Print a closing message
   print "Completed with no errors."
      

########################################################################
# Module entry point
########################################################################

# Run the main routine if the module is executed rather than sourced
if __name__ == '__main__':
   main()

