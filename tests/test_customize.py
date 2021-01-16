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
# Copyright (c) 2010,2015 Kenneth J. Pronovici.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# Version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copies of the GNU General Public License are available from
# the Free Software Foundation website, http://www.gnu.org/.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Python 3 (>= 3.7)
# Project  : Cedar Backup, release 3
# Purpose  : Tests customization functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Unit tests for CedarBackup3/customize.py.
@author Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Import modules and do runtime validations
########################################################################

import unittest

from CedarBackup3.config import CommandOverride, Config, OptionsConfig
from CedarBackup3.customize import PLATFORM, customizeOverrides
from CedarBackup3.testutil import configureLogging

#######################################################################
# Test Case Classes
#######################################################################

######################
# TestFunctions class
######################


class TestFunctions(unittest.TestCase):

    """Tests for the various public functions."""

    ################
    # Setup methods
    ################

    @classmethod
    def setUpClass(cls):
        configureLogging()

    ############################
    # Test customizeOverrides()
    ############################

    def testCustomizeOverrides_001(self):
        """
        Test platform=standard, no existing overrides.
        """
        config = Config()
        options = OptionsConfig()
        if PLATFORM == "standard":
            config.options = options
            customizeOverrides(config)
            self.assertEqual(None, options.overrides)
        config.options = options
        customizeOverrides(config, platform="standard")
        self.assertEqual(None, options.overrides)

    def testCustomizeOverrides_002(self):
        """
        Test platform=standard, existing override for cdrecord.
        """
        config = Config()
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("cdrecord", "/blech"),
        ]
        if PLATFORM == "standard":
            config.options = options
            customizeOverrides(config)
            self.assertEqual([CommandOverride("cdrecord", "/blech")], options.overrides)
        config.options = options
        customizeOverrides(config, platform="standard")
        self.assertEqual([CommandOverride("cdrecord", "/blech")], options.overrides)

    def testCustomizeOverrides_003(self):
        """
        Test platform=standard, existing override for mkisofs.
        """
        config = Config()
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("mkisofs", "/blech"),
        ]
        if PLATFORM == "standard":
            config.options = options
            customizeOverrides(config)
            self.assertEqual([CommandOverride("mkisofs", "/blech")], options.overrides)
        config.options = options
        customizeOverrides(config, platform="standard")
        self.assertEqual([CommandOverride("mkisofs", "/blech")], options.overrides)

    def testCustomizeOverrides_004(self):
        """
        Test platform=standard, existing override for cdrecord and mkisofs.
        """
        config = Config()
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("cdrecord", "/blech"),
            CommandOverride("mkisofs", "/blech2"),
        ]
        if PLATFORM == "standard":
            config.options = options
            customizeOverrides(config)
            self.assertEqual([CommandOverride("cdrecord", "/blech"), CommandOverride("mkisofs", "/blech2")], options.overrides)
        config.options = options
        customizeOverrides(config, platform="standard")
        self.assertEqual([CommandOverride("cdrecord", "/blech"), CommandOverride("mkisofs", "/blech2")], options.overrides)

    def testCustomizeOverrides_005(self):
        """
        Test platform=debian, no existing overrides.
        """
        config = Config()
        options = OptionsConfig()
        if PLATFORM == "debian":
            config.options = options
            customizeOverrides(config)
            self.assertEqual(
                [CommandOverride("cdrecord", "/usr/bin/wodim"), CommandOverride("mkisofs", "/usr/bin/genisoimage")],
                options.overrides,
            )
        config.options = options
        customizeOverrides(config, platform="debian")
        self.assertEqual(
            [CommandOverride("cdrecord", "/usr/bin/wodim"), CommandOverride("mkisofs", "/usr/bin/genisoimage")], options.overrides
        )

    def testCustomizeOverrides_006(self):
        """
        Test platform=debian, existing override for cdrecord.
        """
        config = Config()
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("cdrecord", "/blech"),
        ]
        if PLATFORM == "debian":
            config.options = options
            customizeOverrides(config)
            self.assertEqual(
                [CommandOverride("cdrecord", "/blech"), CommandOverride("mkisofs", "/usr/bin/genisoimage")], options.overrides
            )
        config.options = options
        customizeOverrides(config, platform="debian")
        self.assertEqual(
            [CommandOverride("cdrecord", "/blech"), CommandOverride("mkisofs", "/usr/bin/genisoimage")], options.overrides
        )

    def testCustomizeOverrides_007(self):
        """
        Test platform=debian, existing override for mkisofs.
        """
        config = Config()
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("mkisofs", "/blech"),
        ]
        if PLATFORM == "debian":
            config.options = options
            customizeOverrides(config)
            self.assertEqual(
                [CommandOverride("cdrecord", "/usr/bin/wodim"), CommandOverride("mkisofs", "/blech")], options.overrides
            )
        config.options = options
        customizeOverrides(config, platform="debian")
        self.assertEqual([CommandOverride("cdrecord", "/usr/bin/wodim"), CommandOverride("mkisofs", "/blech")], options.overrides)

    def testCustomizeOverrides_008(self):
        """
        Test platform=debian, existing override for cdrecord and mkisofs.
        """
        config = Config()
        options = OptionsConfig()
        options.overrides = [
            CommandOverride("cdrecord", "/blech"),
            CommandOverride("mkisofs", "/blech2"),
        ]
        if PLATFORM == "debian":
            config.options = options
            customizeOverrides(config)
            self.assertEqual([CommandOverride("cdrecord", "/blech"), CommandOverride("mkisofs", "/blech2")], options.overrides)
        config.options = options
        customizeOverrides(config, platform="debian")
        self.assertEqual([CommandOverride("cdrecord", "/blech"), CommandOverride("mkisofs", "/blech2")], options.overrides)
