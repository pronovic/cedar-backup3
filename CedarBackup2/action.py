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
# Language : Python 3 (>= 3.4.2)
# Project  : Cedar Backup, release 3
# Purpose  : Provides implementation of various backup-related actions.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides interface backwards compatibility.

In Cedar Backup 2.10.0, a refactoring effort took place to reorganize the code
for the standard actions.  The code formerly in action.py was split into
various other files in the CedarBackup2.actions package.  This mostly-empty
file remains to preserve the Cedar Backup library interface.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

# pylint: disable=W0611
from CedarBackup2.actions.collect import executeCollect
from CedarBackup2.actions.stage import executeStage
from CedarBackup2.actions.store import executeStore
from CedarBackup2.actions.purge import executePurge
from CedarBackup2.actions.rebuild import executeRebuild
from CedarBackup2.actions.validate import executeValidate

