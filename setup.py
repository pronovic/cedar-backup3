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
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Python (>= 2.5)
# Project  : Cedar Backup, release 2
# Revision : $Id: setup.py 1093 2014-10-08 02:08:39Z pronovic $
# Purpose  : Python distutils setup script
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# pylint: disable=C0111

########################################################################
# Imported modules
########################################################################

from distutils.core import setup
from CedarBackup2.release import AUTHOR, EMAIL, VERSION, COPYRIGHT, URL


########################################################################
# Setup configuration
########################################################################

LONG_DESCRIPTION = """
Cedar Backup is a software package designed to manage system backups for a
pool of local and remote machines.  Cedar Backup understands how to back up
filesystem data as well as MySQL and PostgreSQL databases and Subversion
repositories.  It can also be easily extended to support other kinds of
data sources.

Cedar Backup is focused around weekly backups to a single CD or DVD disc, with
the expectation that the disc will be changed or overwritten at the beginning
of each week.  If your hardware is new enough, Cedar Backup can write
multisession discs, allowing you to add incremental data to a disc on a daily
basis.

Alternately, Cedar Backup can write your backups to the Amazon S3 cloud
rather than relying on physical media.

Besides offering command-line utilities to manage the backup process, Cedar
Backup provides a well-organized library of backup-related functionality,
written in the Python programming language.
"""

setup (
   name             = 'CedarBackup2',
   version          = VERSION,
   description      = 'Implements local and remote backups to CD/DVD media.',
   long_description = LONG_DESCRIPTION,
   keywords         = ('local', 'remote', 'backup', 'scp', 'CD-R', 'CD-RW', 'DVD+R', 'DVD+RW',), 
   author           = AUTHOR,
   author_email     = EMAIL,
   url              = URL,
   license          = "Copyright (c) %s %s.  Licensed under the GNU GPL." % (COPYRIGHT, AUTHOR),
   platforms        = ('Any',),
   packages         = ['CedarBackup2', 'CedarBackup2.actions', 'CedarBackup2.extend', 
                       'CedarBackup2.tools', 'CedarBackup2.writers', ],
   scripts          = ['cback', 'util/cback-span', 'util/cback-amazons3-sync', ], 
)

