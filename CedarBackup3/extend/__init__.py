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
# Language : Python 3 (>= 3.4)
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

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Package initialization
########################################################################

# Using 'from CedarBackup3.extend import *' will just import the modules listed
# in the __all__ variable.

__all__ = [ 'amazons3', 'encrypt', 'mbox', 'mysql', 'postgresql', 'split', 'subversion', 'sysinfo', ]

