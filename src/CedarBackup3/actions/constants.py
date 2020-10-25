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
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Python 3 (>= 3.7)
# Project  : Cedar Backup, release 3
# Purpose  : Provides common constants used by standard actions.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides common constants used by standard actions.
:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Module-wide constants and variables
########################################################################

DIR_TIME_FORMAT = "%Y/%m/%d"
DIGEST_EXTENSION = "sha"

INDICATOR_PATTERN = [r"cback\..*"]
COLLECT_INDICATOR = "cback.collect"
STAGE_INDICATOR = "cback.stage"
STORE_INDICATOR = "cback.store"
