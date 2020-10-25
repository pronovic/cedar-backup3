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
# Project  : Official Cedar Backup Extensions
# Purpose  : Provides package initialization
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Official Cedar Backup Extensions

This package provides official Cedar Backup extensions.  These are Cedar Backup
actions that are not part of the "standard" set of Cedar Backup actions, but
are officially supported along with Cedar Backup.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Package initialization
########################################################################

# Using 'from CedarBackup3.extend import *' will just import the modules listed
# in the __all__ variable.

import CedarBackup3.extend.amazons3
import CedarBackup3.extend.encrypt
import CedarBackup3.extend.mbox
import CedarBackup3.extend.mysql
import CedarBackup3.extend.postgresql
import CedarBackup3.extend.split
import CedarBackup3.extend.subversion
import CedarBackup3.extend.sysinfo

__all__ = ["amazons3", "encrypt", "mbox", "mysql", "postgresql", "split", "subversion", "sysinfo"]
