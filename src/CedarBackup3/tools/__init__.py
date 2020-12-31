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
like the main ``cback3`` script.  Like the ``cback3`` script, the majority of a
tool is implemented in a .py module, and then the script just invokes the
module's ``cli()`` function.  The actual scripts for tools are distributed in
the util/ directory.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Package initialization
########################################################################

# Using 'from CedarBackup3.tools import *' will just import the modules listed
# in the __all__ variable.

import CedarBackup3.tools.amazons3
import CedarBackup3.tools.span

__all__ = ["span", "amazons3"]
