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
# Revision : $Id: image.py 1022 2011-10-11 23:27:49Z pronovic $
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

from CedarBackup2.writers.util import IsoImage  # pylint: disable=W0611

