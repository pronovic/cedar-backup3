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
# Revision : $Id: constants.py 998 2010-07-07 19:56:08Z pronovic $
# Purpose  : Provides common constants used by standard actions.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides common constants used by standard actions.
@sort: DIR_TIME_FORMAT, DIGEST_EXTENSION, INDICATOR_PATTERN,
       COLLECT_INDICATOR, STAGE_INDICATOR, STORE_INDICATOR
@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Module-wide constants and variables
########################################################################

DIR_TIME_FORMAT      = "%Y/%m/%d"
DIGEST_EXTENSION     = "sha"

INDICATOR_PATTERN    = [ "cback\..*", ]
COLLECT_INDICATOR    = "cback.collect"
STAGE_INDICATOR      = "cback.stage"
STORE_INDICATOR      = "cback.store"

