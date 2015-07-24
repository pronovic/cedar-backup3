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
# Project  : Official Cedar Backup Extensions
# Revision : $Id: __init__.py 998 2010-07-07 19:56:08Z pronovic $
# Purpose  : Provides package initialization
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Cedar Backup writers.

This package consolidates all of the modules that implenent "image writer"
functionality, including utilities and specific writer implementations.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Package initialization
########################################################################

# Using 'from CedarBackup2.writers import *' will just import the modules listed
# in the __all__ variable.

__all__ = [ 'util', 'cdwriter', 'dvdwriter', ]

