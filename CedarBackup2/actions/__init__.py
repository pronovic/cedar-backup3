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
# Project  : Official Cedar Backup Extensions
# Purpose  : Provides package initialization
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Cedar Backup actions.

This package code related to the offical Cedar Backup actions (collect,
stage, store, purge, rebuild, and validate).

The action modules consist of mostly "glue" code that uses other lower-level
functionality to actually implement a backup.  There is one module for each
high-level backup action, plus a module that provides shared constants.

All of the public action function implement the Cedar Backup Extension
Architecture Interface, i.e. the same interface that extensions implement.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Package initialization
########################################################################

# Using 'from CedarBackup2.actions import *' will just import the modules listed
# in the __all__ variable.

__all__ = [ 'constants', 'collect', 'initialize', 'stage', 'store', 'purge', 'util', 'rebuild', 'validate', ]

