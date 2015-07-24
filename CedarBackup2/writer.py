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
# Purpose  : Provides interface backwards compatibility.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides interface backwards compatibility.

In Cedar Backup 2.10.0, a refactoring effort took place while adding code to
support DVD hardware.  All of the writer functionality was moved to the
writers/ package.  This mostly-empty file remains to preserve the Cedar Backup
library interface.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

# pylint: disable=W0611
from CedarBackup2.writers.util import validateScsiId, validateDriveSpeed
from CedarBackup2.writers.cdwriter import MediaDefinition, MediaCapacity, CdWriter
from CedarBackup2.writers.cdwriter import MEDIA_CDRW_74, MEDIA_CDR_74, MEDIA_CDRW_80, MEDIA_CDR_80

