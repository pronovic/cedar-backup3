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
# Project  : Official Cedar Backup Tools
# Purpose  : Provides package initialization
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Official Cedar Backup Tools

This package provides official Cedar Backup tools.  Tools are things that feel
a little like extensions, but don't fit the normal mold of extensions.  For
instance, they might not be intended to run from cron, or might need to interact
dynamically with the user (i.e. accept user input).

Tools are usually scripts that are run directly from the command line, just
like the main C{cback3} script.  Like the C{cback3} script, the majority of a
tool is implemented in a .py module, and then the script just invokes the
module's C{cli()} function.  The actual scripts for tools are distributed in
the util/ directory.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Package initialization
########################################################################

# Using 'from CedarBackup3.tools import *' will just import the modules listed
# in the __all__ variable.

__all__ = [ 'span', 'amazons3', ]

