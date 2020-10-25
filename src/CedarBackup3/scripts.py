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
# Purpose  : Scripts published by Poetry as part of the Python package
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

"""
Scripts published by Poetry as part of the Python package.
"""

import sys


def cback3():
    """Implementation of the cback3 script, the main command-line interface."""
    from CedarBackup3.cli import cli  # pylint: disable=import-outside-toplevel

    result = cli()
    sys.exit(result)


def amazons3():
    """Implementation of the cback3-amazons3-sync script."""
    from CedarBackup3.tools.amazons3 import cli  # pylint: disable=import-outside-toplevel

    result = cli()
    sys.exit(result)


def span():
    """Implementation of the cback3-span script."""
    from CedarBackup3.tools.span import cli  # pylint: disable=import-outside-toplevel

    result = cli()
    sys.exit(result)
