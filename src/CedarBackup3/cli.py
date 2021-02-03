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
# Copyright (c) 2004-2007,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides command-line interface implementation.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides command-line interface implementation for the cback3 script.

Summary
=======

   The functionality in this module encapsulates the command-line interface for
   the cback3 script.  The cback3 script itself is very short, basically just an
   invokation of one function implemented here.  That, in turn, makes it
   simpler to validate the command line interface (for instance, it's easier to
   run pychecker against a module, and unit tests are easier, too).

   The objects and functions implemented in this module are probably not useful
   to any code external to Cedar Backup.   Anyone else implementing their own
   command-line interface would have to reimplement (or at least enhance) all
   of this anyway.

Backwards Compatibility
=======================

   The command line interface has changed between Cedar Backup 1.x and Cedar
   Backup 2.x.  Some new switches have been added, and the actions have become
   simple arguments rather than switches (which is a much more standard command
   line format).  Old 1.x command lines are generally no longer valid.

Module Attributes
=================

Attributes:
   DEFAULT_CONFIG: The default configuration file
   DEFAULT_LOGFILE: The default log file path
   DEFAULT_OWNERSHIP: Default ownership for the logfile
   DEFAULT_MODE: Default file permissions mode on the logfile
   VALID_ACTIONS: List of valid actions
   COMBINE_ACTIONS: List of actions which can be combined with other actions
   NONCOMBINE_ACTIONS: List of actions which cannot be combined with other actions

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

########################################################################
# Imported modules
########################################################################

import getopt
import logging
import os
import sys
from functools import total_ordering

from CedarBackup3.actions.collect import executeCollect
from CedarBackup3.actions.initialize import executeInitialize
from CedarBackup3.actions.purge import executePurge
from CedarBackup3.actions.rebuild import executeRebuild
from CedarBackup3.actions.stage import executeStage
from CedarBackup3.actions.store import executeStore
from CedarBackup3.actions.validate import executeValidate
from CedarBackup3.config import Config
from CedarBackup3.customize import customizeOverrides
from CedarBackup3.peer import RemotePeer
from CedarBackup3.release import AUTHOR, COPYRIGHT, DATE, EMAIL, VERSION
from CedarBackup3.util import (
    Diagnostics,
    DirectedGraph,
    PathResolverSingleton,
    encodePath,
    executeCommand,
    getFunctionReference,
    getUidGid,
    sortDict,
    splitCommandLine,
)

########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.cli")

DISK_LOG_FORMAT = "%(asctime)s --> [%(levelname)-7s] %(message)s"
DISK_OUTPUT_FORMAT = "%(message)s"
SCREEN_LOG_FORMAT = "%(message)s"
SCREEN_LOG_STREAM = sys.stdout
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S %Z"

DEFAULT_CONFIG = "/etc/cback3.conf"
DEFAULT_LOGFILE = "/var/log/cback3.log"
DEFAULT_OWNERSHIP = ["root", "adm"]
DEFAULT_MODE = 0o640

REBUILD_INDEX = 0  # can't run with anything else, anyway
VALIDATE_INDEX = 0  # can't run with anything else, anyway
INITIALIZE_INDEX = 0  # can't run with anything else, anyway
COLLECT_INDEX = 100
STAGE_INDEX = 200
STORE_INDEX = 300
PURGE_INDEX = 400

VALID_ACTIONS = ["collect", "stage", "store", "purge", "rebuild", "validate", "initialize", "all"]
COMBINE_ACTIONS = ["collect", "stage", "store", "purge"]
NONCOMBINE_ACTIONS = ["rebuild", "validate", "initialize", "all"]

SHORT_SWITCHES = "hVbqc:fMNl:o:m:OdsD"
LONG_SWITCHES = [
    "help",
    "version",
    "verbose",
    "quiet",
    "config=",
    "full",
    "managed",
    "managed-only",
    "logfile=",
    "owner=",
    "mode=",
    "output",
    "debug",
    "stack",
    "diagnostics",
]


#######################################################################
# Public functions
#######################################################################

#################
# cli() function
#################


def cli():
    """
    Implements the command-line interface for the ``cback3`` script.

    Essentially, this is the "main routine" for the cback3 script.  It does all
    of the argument processing for the script, and then sets about executing the
    indicated actions.

    As a general rule, only the actions indicated on the command line will be
    executed.   We will accept any of the built-in actions and any of the
    configured extended actions (which makes action list verification a two-
    step process).

    The ``'all'`` action has a special meaning: it means that the built-in set of
    actions (collect, stage, store, purge) will all be executed, in that order.
    Extended actions will be ignored as part of the ``'all'`` action.

    Raised exceptions always result in an immediate return.  Otherwise, we
    generally return when all specified actions have been completed.  Actions
    are ignored if the help, version or validate flags are set.

    A different error code is returned for each type of failure:

       - ``1``: The Python interpreter version is < 3.7
       - ``2``: Error processing command-line arguments
       - ``3``: Error configuring logging
       - ``4``: Error parsing indicated configuration file
       - ``5``: Backup was interrupted with a CTRL-C or similar
       - ``6``: Error executing specified backup actions

    *Note:* This function contains a good amount of logging at the INFO level,
    because this is the right place to document high-level flow of control (i.e.
    what the command-line options were, what config file was being used, etc.)

    *Note:* We assume that anything that *must* be seen on the screen is logged
    at the ERROR level.  Errors that occur before logging can be configured are
    written to ``sys.stderr``.

    Returns:
        Error code as described above
    """
    try:
        if list(map(int, [sys.version_info[0], sys.version_info[1]])) < [3, 7]:
            sys.stderr.write("Python 3 version 3.7 or greater required.\n")
            return 1
    except:
        # sys.version_info isn't available before 2.0
        sys.stderr.write("Python 3 version 3.7 or greater required.\n")
        return 1

    try:
        options = Options(argumentList=sys.argv[1:])
        logger.info("Specified command-line actions: %s", options.actions)
    except Exception as e:
        _usage()
        sys.stderr.write(" *** Error: %s\n" % e)
        return 2

    if options.help:
        _usage()
        return 0
    if options.version:
        _version()
        return 0
    if options.diagnostics:
        _diagnostics()
        return 0

    if options.stacktrace:
        logfile = setupLogging(options)
    else:
        try:
            logfile = setupLogging(options)
        except Exception as e:
            sys.stderr.write("Error setting up logging: %s\n" % e)
            return 3

    logger.info("Cedar Backup run started.")
    logger.info("Options were [%s]", options)
    logger.info("Logfile is [%s]", logfile)
    Diagnostics().logDiagnostics(method=logger.info)

    if options.config is None:
        logger.debug("Using default configuration file.")
        configPath = DEFAULT_CONFIG
    else:
        logger.debug("Using user-supplied configuration file.")
        configPath = options.config

    executeLocal = True
    executeManaged = False
    if options.managedOnly:
        executeLocal = False
        executeManaged = True
    if options.managed:
        executeManaged = True
    logger.debug("Execute local actions: %s", executeLocal)
    logger.debug("Execute managed actions: %s", executeManaged)

    try:
        logger.info("Configuration path is [%s]", configPath)
        config = Config(xmlPath=configPath)
        customizeOverrides(config)
        setupPathResolver(config)
        actionSet = _ActionSet(options.actions, config.extensions, config.options, config.peers, executeManaged, executeLocal)
    except Exception as e:
        logger.error("Error reading or handling configuration: %s", e)
        logger.info("Cedar Backup run completed with status 4.")
        return 4

    if options.stacktrace:
        actionSet.executeActions(configPath, options, config)
    else:
        try:
            actionSet.executeActions(configPath, options, config)
        except KeyboardInterrupt:
            logger.error("Backup interrupted.")
            logger.info("Cedar Backup run completed with status 5.")
            return 5
        except Exception as e:
            logger.error("Error executing backup: %s", e)
            logger.info("Cedar Backup run completed with status 6.")
            return 6

    logger.info("Cedar Backup run completed with status 0.")
    return 0


########################################################################
# Action-related class definition
########################################################################

####################
# _ActionItem class
####################


@total_ordering
class _ActionItem(object):

    """
    Class representing a single action to be executed.

    This class represents a single named action to be executed, and understands
    how to execute that action.

    The built-in actions will use only the options and config values.  We also
    pass in the config path so that extension modules can re-parse configuration
    if they want to, to add in extra information.

    This class is also where pre-action and post-action hooks are executed.  An
    action item is instantiated in terms of optional pre- and post-action hook
    objects (config.ActionHook), which are then executed at the appropriate time
    (if set).

    *Note:* The comparison operators for this class have been implemented to only
    compare based on the index and SORT_ORDER value, and ignore all other
    values.  This is so that the action set list can be easily sorted first by
    type (_ActionItem before _ManagedActionItem) and then by index within type.

    Attributes:
       SORT_ORDER: Defines a sort order to order properly between types
    """

    SORT_ORDER = 0

    def __init__(self, index, name, preHooks, postHooks, function):
        """
        Default constructor.

        It's OK to pass ``None`` for ``index``, ``preHooks`` or ``postHooks``, but not
        for ``name``.

        Args:
           index: Index of the item (or ``None``)
           name: Name of the action that is being executed
           preHooks: List of pre-action hooks in terms of an ``ActionHook`` object, or ``None``
           postHooks: List of post-action hooks in terms of an ``ActionHook`` object, or ``None``
           function: Reference to function associated with item
        """
        self.index = index
        self.name = name
        self.preHooks = preHooks
        self.postHooks = postHooks
        self.function = function

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        The only thing we compare is the item's index.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.index != other.index:
            if int(self.index or 0) < int(other.index or 0):
                return -1
            else:
                return 1
        else:
            if self.SORT_ORDER != other.SORT_ORDER:
                if int(self.SORT_ORDER or 0) < int(other.SORT_ORDER or 0):
                    return -1
                else:
                    return 1
        return 0

    def executeAction(self, configPath, options, config):
        """
        Executes the action associated with an item, including hooks.

        See class notes for more details on how the action is executed.

        Args:
           configPath: Path to configuration file on disk
           options: Command-line options to be passed to action
           config: Parsed configuration to be passed to action

        Raises:
           Exception: If there is a problem executing the action
        """
        logger.debug("Executing [%s] action.", self.name)
        if self.preHooks is not None:
            for hook in self.preHooks:
                self._executeHook("pre-action", hook)
        self._executeAction(configPath, options, config)
        if self.postHooks is not None:
            for hook in self.postHooks:
                self._executeHook("post-action", hook)

    def _executeAction(self, configPath, options, config):
        """
        Executes the action, specifically the function associated with the action.
        Args:
           configPath: Path to configuration file on disk
           options: Command-line options to be passed to action
           config: Parsed configuration to be passed to action
        """
        name = "%s.%s" % (self.function.__module__, self.function.__name__)
        logger.debug("Calling action function [%s], execution index [%d]", name, self.index)
        self.function(configPath, options, config)

    def _executeHook(self, type, hook):  # pylint: disable=W0622,R0201
        """
        Executes a hook command via :any:`util.executeCommand`.
        Args:
           type: String describing the type of hook, for logging
           hook: Hook, in terms of a ``ActionHook`` object
        """
        fields = splitCommandLine(hook.command)
        logger.debug("Executing %s hook for action [%s]: %s", type, hook.action, fields[0:1])
        result, output = executeCommand(command=fields[0:1], args=fields[1:], returnOutput=True)
        if result != 0:
            logger.debug("Hook failed, tail is: %s", "\n   %s" % "   ".join(output[-10:]) if output else "<empty>")
            raise IOError("Error (%d) executing %s hook for action [%s]: %s" % (result, type, hook.action, fields[0:1]))


###########################
# _ManagedActionItem class
###########################


@total_ordering
class _ManagedActionItem(object):

    """
    Class representing a single action to be executed on a managed peer.

    This class represents a single named action to be executed, and understands
    how to execute that action.

    Actions to be executed on a managed peer rely on peer configuration and
    on the full-backup flag.  All other configuration takes place on the remote
    peer itself.

    *Note:* The comparison operators for this class have been implemented to only
    compare based on the index and SORT_ORDER value, and ignore all other
    values.  This is so that the action set list can be easily sorted first by
    type (_ActionItem before _ManagedActionItem) and then by index within type.

    Attributes:
       SORT_ORDER: Defines a sort order to order properly between types
    """

    SORT_ORDER = 1

    def __init__(self, index, name, remotePeers):
        """
        Default constructor.

        Args:
           index: Index of the item (or ``None``)
           name: Name of the action that is being executed
           remotePeers: List of remote peers on which to execute the action
        """
        self.index = index
        self.name = name
        self.remotePeers = remotePeers

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        The only thing we compare is the item's index.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.index != other.index:
            if int(self.index or 0) < int(other.index or 0):
                return -1
            else:
                return 1
        else:
            if self.SORT_ORDER != other.SORT_ORDER:
                if int(self.SORT_ORDER or 0) < int(other.SORT_ORDER or 0):
                    return -1
                else:
                    return 1
        return 0

    # pylint: disable=W0613
    def executeAction(self, configPath, options, config):
        """
        Executes the managed action associated with an item.

        *Note:* Only options.full is actually used.  The rest of the arguments
        exist to satisfy the ActionItem iterface.

        *Note:* Errors here result in a message logged to ERROR, but no thrown
        exception.  The analogy is the stage action where a problem with one host
        should not kill the entire backup.  Since we're logging an error, the
        administrator will get an email.

        Args:
           configPath: Path to configuration file on disk
           options: Command-line options to be passed to action
           config: Parsed configuration to be passed to action

        Raises:
           Exception: If there is a problem executing the action
        """
        for peer in self.remotePeers:
            logger.debug("Executing managed action [%s] on peer [%s].", self.name, peer.name)
            try:
                peer.executeManagedAction(self.name, options.full)
            except IOError as e:
                logger.error(e)  # log the message and go on, so we don't kill the backup


###################
# _ActionSet class
###################


class _ActionSet(object):

    """
    Class representing a set of local actions to be executed.

    This class does four different things.  First, it ensures that the actions
    specified on the command-line are sensible.  The command-line can only list
    either built-in actions or extended actions specified in configuration.
    Also, certain actions (in :any:`NONCOMBINE_ACTIONS`) cannot be combined with
    other actions.

    Second, the class enforces an execution order on the specified actions.  Any
    time actions are combined on the command line (either built-in actions or
    extended actions), we must make sure they get executed in a sensible order.

    Third, the class ensures that any pre-action or post-action hooks are
    scheduled and executed appropriately.  Hooks are configured by building a
    dictionary mapping between hook action name and command.  Pre-action hooks
    are executed immediately before their associated action, and post-action
    hooks are executed immediately after their associated action.

    Finally, the class properly interleaves local and managed actions so that
    the same action gets executed first locally and then on managed peers.

    """

    def __init__(self, actions, extensions, options, peers, managed, local):
        """
        Constructor for the ``_ActionSet`` class.

        This is kind of ugly, because the constructor has to set up a lot of data
        before being able to do anything useful.  The following data structures
        are initialized based on the input:

           - ``extensionNames``: List of extensions available in configuration
           - ``preHookMap``: Mapping from action name to list of ``PreActionHook``
           - ``postHookMap``: Mapping from action name to list of ``PostActionHook``
           - ``functionMap``: Mapping from action name to Python function
           - ``indexMap``: Mapping from action name to execution index
           - ``peerMap``: Mapping from action name to set of ``RemotePeer``
           - ``actionMap``: Mapping from action name to ``_ActionItem``

        Once these data structures are set up, the command line is validated to
        make sure only valid actions have been requested, and in a sensible
        combination.  Then, all of the data is used to build ``self.actionSet``,
        the set action items to be executed by ``executeActions()``.  This list
        might contain either ``_ActionItem`` or ``_ManagedActionItem``.

        Args:
           actions: Names of actions specified on the command-line
           extensions: Extended action configuration (i.e. config.extensions)
           options: Options configuration (i.e. config.options)
           peers: Peers configuration (i.e. config.peers)
           managed: Whether to include managed actions in the set
           local: Whether to include local actions in the set

        Raises:
           ValueError: If one of the specified actions is invalid
        """
        extensionNames = _ActionSet._deriveExtensionNames(extensions)
        (preHookMap, postHookMap) = _ActionSet._buildHookMaps(options.hooks)
        functionMap = _ActionSet._buildFunctionMap(extensions)
        indexMap = _ActionSet._buildIndexMap(extensions)
        peerMap = _ActionSet._buildPeerMap(options, peers)
        actionMap = _ActionSet._buildActionMap(
            managed, local, extensionNames, functionMap, indexMap, preHookMap, postHookMap, peerMap
        )
        _ActionSet._validateActions(actions, extensionNames)
        self.actionSet = _ActionSet._buildActionSet(actions, actionMap)

    @staticmethod
    def _deriveExtensionNames(extensions):
        """
        Builds a list of extended actions that are available in configuration.
        Args:
           extensions: Extended action configuration (i.e. config.extensions)
        Returns:
            List of extended action names
        """
        extensionNames = []
        if extensions is not None and extensions.actions is not None:
            for action in extensions.actions:
                extensionNames.append(action.name)
        return extensionNames

    @staticmethod
    def _buildHookMaps(hooks):
        """
        Build two mappings from action name to configured ``ActionHook``.
        Args:
           hooks: List of pre- and post-action hooks (i.e. config.options.hooks)
        Returns:
            Tuple of (pre hook dictionary, post hook dictionary)
        """
        preHookMap = {}
        postHookMap = {}
        if hooks is not None:
            for hook in hooks:
                if hook.before:
                    if hook.action not in preHookMap:
                        preHookMap[hook.action] = []
                    preHookMap[hook.action].append(hook)
                elif hook.after:
                    if hook.action not in postHookMap:
                        postHookMap[hook.action] = []
                    postHookMap[hook.action].append(hook)
        return (preHookMap, postHookMap)

    @staticmethod
    def _buildFunctionMap(extensions):
        """
        Builds a mapping from named action to action function.
        Args:
           extensions: Extended action configuration (i.e. config.extensions)
        Returns:
            Dictionary mapping action to function
        """
        functionMap = {}
        functionMap["rebuild"] = executeRebuild
        functionMap["validate"] = executeValidate
        functionMap["initialize"] = executeInitialize
        functionMap["collect"] = executeCollect
        functionMap["stage"] = executeStage
        functionMap["store"] = executeStore
        functionMap["purge"] = executePurge
        if extensions is not None and extensions.actions is not None:
            for action in extensions.actions:
                functionMap[action.name] = getFunctionReference(action.module, action.function)
        return functionMap

    @staticmethod
    def _buildIndexMap(extensions):
        """
        Builds a mapping from action name to proper execution index.

        If extensions configuration is ``None``, or there are no configured
        extended actions, the ordering dictionary will only include the built-in
        actions and their standard indices.

        Otherwise, if the extensions order mode is ``None`` or ``"index"``, actions
        will scheduled by explicit index; and if the extensions order mode is
        ``"dependency"``, actions will be scheduled using a dependency graph.

        Args:
           extensions: Extended action configuration (i.e. config.extensions)

        Returns:
            Dictionary mapping action name to integer execution index
        """
        indexMap = {}
        if extensions is None or extensions.actions is None or extensions.actions == []:
            logger.info("Action ordering will use 'index' order mode.")
            indexMap["rebuild"] = REBUILD_INDEX
            indexMap["validate"] = VALIDATE_INDEX
            indexMap["initialize"] = INITIALIZE_INDEX
            indexMap["collect"] = COLLECT_INDEX
            indexMap["stage"] = STAGE_INDEX
            indexMap["store"] = STORE_INDEX
            indexMap["purge"] = PURGE_INDEX
            logger.debug("Completed filling in action indices for built-in actions.")
            logger.info("Action order will be: %s", sortDict(indexMap))
        else:
            if extensions.orderMode is None or extensions.orderMode == "index":
                logger.info("Action ordering will use 'index' order mode.")
                indexMap["rebuild"] = REBUILD_INDEX
                indexMap["validate"] = VALIDATE_INDEX
                indexMap["initialize"] = INITIALIZE_INDEX
                indexMap["collect"] = COLLECT_INDEX
                indexMap["stage"] = STAGE_INDEX
                indexMap["store"] = STORE_INDEX
                indexMap["purge"] = PURGE_INDEX
                logger.debug("Completed filling in action indices for built-in actions.")
                for action in extensions.actions:
                    indexMap[action.name] = action.index
                logger.debug("Completed filling in action indices for extended actions.")
                logger.info("Action order will be: %s", sortDict(indexMap))
            else:
                logger.info("Action ordering will use 'dependency' order mode.")
                graph = DirectedGraph("dependencies")
                graph.createVertex("rebuild")
                graph.createVertex("validate")
                graph.createVertex("initialize")
                graph.createVertex("collect")
                graph.createVertex("stage")
                graph.createVertex("store")
                graph.createVertex("purge")
                for action in extensions.actions:
                    graph.createVertex(action.name)
                graph.createEdge("collect", "stage")  # Collect must run before stage, store or purge
                graph.createEdge("collect", "store")
                graph.createEdge("collect", "purge")
                graph.createEdge("stage", "store")  # Stage must run before store or purge
                graph.createEdge("stage", "purge")
                graph.createEdge("store", "purge")  # Store must run before purge
                for action in extensions.actions:
                    if action.dependencies.beforeList is not None:
                        for vertex in action.dependencies.beforeList:
                            try:
                                graph.createEdge(action.name, vertex)  # actions that this action must be run before
                            except ValueError:
                                logger.error("Dependency [%s] on extension [%s] is unknown.", vertex, action.name)
                                raise ValueError("Unable to determine proper action order due to invalid dependency.")
                    if action.dependencies.afterList is not None:
                        for vertex in action.dependencies.afterList:
                            try:
                                graph.createEdge(vertex, action.name)  # actions that this action must be run after
                            except ValueError:
                                logger.error("Dependency [%s] on extension [%s] is unknown.", vertex, action.name)
                                raise ValueError("Unable to determine proper action order due to invalid dependency.")
                try:
                    ordering = graph.topologicalSort()
                    indexMap = dict([(ordering[i], i + 1) for i in range(0, len(ordering))])
                    logger.info("Action order will be: %s", ordering)
                except ValueError:
                    logger.error("Unable to determine proper action order due to dependency recursion.")
                    logger.error("Extensions configuration is invalid (check for loops).")
                    raise ValueError("Unable to determine proper action order due to dependency recursion.")
        return indexMap

    @staticmethod
    def _buildActionMap(managed, local, extensionNames, functionMap, indexMap, preHookMap, postHookMap, peerMap):
        """
        Builds a mapping from action name to list of action items.

        We build either ``_ActionItem`` or ``_ManagedActionItem`` objects here.

        In most cases, the mapping from action name to ``_ActionItem`` is 1:1.
        The exception is the "all" action, which is a special case.  However, a
        list is returned in all cases, just for consistency later.  Each
        ``_ActionItem`` will be created with a proper function reference and index
        value for execution ordering.

        The mapping from action name to ``_ManagedActionItem`` is always 1:1.
        Each managed action item contains a list of peers which the action should
        be executed.

        Args:
           managed: Whether to include managed actions in the set
           local: Whether to include local actions in the set
           extensionNames: List of valid extended action names
           functionMap: Dictionary mapping action name to Python function
           indexMap: Dictionary mapping action name to integer execution index
           preHookMap: Dictionary mapping action name to pre hooks (if any) for the action
           postHookMap: Dictionary mapping action name to post hooks (if any) for the action
           peerMap: Dictionary mapping action name to list of remote peers on which to execute the action

        Returns:
            Dictionary mapping action name to list of ``_ActionItem`` objects
        """
        actionMap = {}
        for name in extensionNames + VALID_ACTIONS:
            if name != "all":  # do this one later
                function = functionMap[name]
                index = indexMap[name]
                actionMap[name] = []
                if local:
                    (preHooks, postHooks) = _ActionSet._deriveHooks(name, preHookMap, postHookMap)
                    actionMap[name].append(_ActionItem(index, name, preHooks, postHooks, function))
                if managed:
                    if name in peerMap:
                        actionMap[name].append(_ManagedActionItem(index, name, peerMap[name]))
        actionMap["all"] = actionMap["collect"] + actionMap["stage"] + actionMap["store"] + actionMap["purge"]
        return actionMap

    @staticmethod
    def _buildPeerMap(options, peers):
        """
        Build a mapping from action name to list of remote peers.

        There will be one entry in the mapping for each managed action.  If there
        are no managed peers, the mapping will be empty.  Only managed actions
        will be listed in the mapping.

        Args:
           options: Option configuration (i.e. config.options)
           peers: Peers configuration (i.e. config.peers)
        """
        peerMap = {}
        if peers is not None:
            if peers.remotePeers is not None:
                for peer in peers.remotePeers:
                    if peer.managed:
                        remoteUser = _ActionSet._getRemoteUser(options, peer)
                        rshCommand = _ActionSet._getRshCommand(options, peer)
                        cbackCommand = _ActionSet._getCbackCommand(options, peer)
                        managedActions = _ActionSet._getManagedActions(options, peer)
                        remotePeer = RemotePeer(
                            peer.name, None, options.workingDir, remoteUser, None, options.backupUser, rshCommand, cbackCommand
                        )
                        if managedActions is not None:
                            for managedAction in managedActions:
                                if managedAction in peerMap:
                                    if remotePeer not in peerMap[managedAction]:
                                        peerMap[managedAction].append(remotePeer)
                                else:
                                    peerMap[managedAction] = [remotePeer]
        return peerMap

    @staticmethod
    def _deriveHooks(action, preHookDict, postHookDict):
        """
        Derive pre- and post-action hooks, if any, associated with named action.
        Args:
           action: Name of action to look up
           preHookDict: Dictionary mapping pre-action hooks to action name
           postHookDict: Dictionary mapping post-action hooks to action name
        @return Tuple (preHooks, postHooks) per mapping, with None values if there is no hook
        """
        preHooks = None
        postHooks = None
        if action in preHookDict:
            preHooks = preHookDict[action]
        if action in postHookDict:
            postHooks = postHookDict[action]
        return (preHooks, postHooks)

    @staticmethod
    def _validateActions(actions, extensionNames):
        """
        Validate that the set of specified actions is sensible.

        Any specified action must either be a built-in action or must be among
        the extended actions defined in configuration.  The actions from within
        :any:`NONCOMBINE_ACTIONS` may not be combined with other actions.

        Args:
           actions: Names of actions specified on the command-line
           extensionNames: Names of extensions specified in configuration

        Raises:
           ValueError: If one or more configured actions are not valid
        """
        if actions is None or actions == []:
            raise ValueError("No actions specified.")
        for action in actions:
            if action not in VALID_ACTIONS and action not in extensionNames:
                raise ValueError("Action [%s] is not a valid action or extended action." % action)
        for action in NONCOMBINE_ACTIONS:
            if action in actions and actions != [action]:
                raise ValueError("Action [%s] may not be combined with other actions." % action)

    @staticmethod
    def _buildActionSet(actions, actionMap):
        """
        Build set of actions to be executed.

        The set of actions is built in the proper order, so ``executeActions`` can
        spin through the set without thinking about it.  Since we've already validated
        that the set of actions is sensible, we don't take any precautions here to
        make sure things are combined properly.  If the action is listed, it will
        be "scheduled" for execution.

        Args:
           actions: Names of actions specified on the command-line
           actionMap: Dictionary mapping action name to ``_ActionItem`` object

        Returns:
            Set of action items in proper order
        """
        actionSet = []
        for action in actions:
            actionSet.extend(actionMap[action])
        actionSet.sort()  # sort the actions in order by index
        return actionSet

    def executeActions(self, configPath, options, config):
        """
        Executes all actions and extended actions, in the proper order.

        Each action (whether built-in or extension) is executed in an identical
        manner.  The built-in actions will use only the options and config
        values.  We also pass in the config path so that extension modules can
        re-parse configuration if they want to, to add in extra information.

        Args:
           configPath: Path to configuration file on disk
           options: Command-line options to be passed to action functions
           config: Parsed configuration to be passed to action functions

        Raises:
           Exception: If there is a problem executing the actions
        """
        logger.debug("Executing local actions.")
        for actionItem in self.actionSet:
            actionItem.executeAction(configPath, options, config)

    @staticmethod
    def _getRemoteUser(options, remotePeer):
        """
        Gets the remote user associated with a remote peer.
        Use peer's if possible, otherwise take from options section.
        Args:
           options: OptionsConfig object, as from config.options
           remotePeer: Configuration-style remote peer object
        Returns:
            Name of remote user associated with remote peer
        """
        if remotePeer.remoteUser is None:
            return options.backupUser
        return remotePeer.remoteUser

    @staticmethod
    def _getRshCommand(options, remotePeer):
        """
        Gets the RSH command associated with a remote peer.
        Use peer's if possible, otherwise take from options section.
        Args:
           options: OptionsConfig object, as from config.options
           remotePeer: Configuration-style remote peer object
        Returns:
            RSH command associated with remote peer
        """
        if remotePeer.rshCommand is None:
            return options.rshCommand
        return remotePeer.rshCommand

    @staticmethod
    def _getCbackCommand(options, remotePeer):
        """
        Gets the cback command associated with a remote peer.
        Use peer's if possible, otherwise take from options section.
        Args:
           options: OptionsConfig object, as from config.options
           remotePeer: Configuration-style remote peer object
        Returns:
            cback command associated with remote peer
        """
        if remotePeer.cbackCommand is None:
            return options.cbackCommand
        return remotePeer.cbackCommand

    @staticmethod
    def _getManagedActions(options, remotePeer):
        """
        Gets the managed actions list associated with a remote peer.
        Use peer's if possible, otherwise take from options section.
        Args:
           options: OptionsConfig object, as from config.options
           remotePeer: Configuration-style remote peer object
        Returns:
            Set of managed actions associated with remote peer
        """
        if remotePeer.managedActions is None:
            return options.managedActions
        return remotePeer.managedActions


#######################################################################
# Utility functions
#######################################################################

####################
# _usage() function
####################


def _usage(fd=sys.stderr):
    """
    Prints usage information for the cback3 script.
    Args:
       fd: File descriptor used to print information
    *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
    """
    fd.write("\n")
    fd.write(" Usage: cback3 [switches] action(s)\n")
    fd.write("\n")
    fd.write(" The following switches are accepted:\n")
    fd.write("\n")
    fd.write("   -h, --help         Display this usage/help listing\n")
    fd.write("   -V, --version      Display version information\n")
    fd.write("   -b, --verbose      Print verbose output as well as logging to disk\n")
    fd.write("   -q, --quiet        Run quietly (display no output to the screen)\n")
    fd.write("   -c, --config       Path to config file (default: %s)\n" % DEFAULT_CONFIG)
    fd.write("   -f, --full         Perform a full backup, regardless of configuration\n")
    fd.write("   -M, --managed      Include managed clients when executing actions\n")
    fd.write("   -N, --managed-only Include ONLY managed clients when executing actions\n")
    fd.write("   -l, --logfile      Path to logfile (default: %s)\n" % DEFAULT_LOGFILE)
    fd.write(
        "   -o, --owner        Logfile ownership, user:group (default: %s:%s)\n" % (DEFAULT_OWNERSHIP[0], DEFAULT_OWNERSHIP[1])
    )
    fd.write("   -m, --mode         Octal logfile permissions mode (default: %o)\n" % DEFAULT_MODE)
    fd.write("   -O, --output       Record some sub-command (i.e. cdrecord) output to the log\n")
    fd.write("   -d, --debug        Write debugging information to the log (implies --output)\n")
    fd.write(
        "   -s, --stack        Dump a Python stack trace instead of swallowing exceptions\n"
    )  # exactly 80 characters in width!
    fd.write("   -D, --diagnostics  Print runtime diagnostics to the screen and exit\n")
    fd.write("\n")
    fd.write(" The following actions may be specified:\n")
    fd.write("\n")
    fd.write("   all                Take all normal actions (collect, stage, store, purge)\n")
    fd.write("   collect            Take the collect action\n")
    fd.write("   stage              Take the stage action\n")
    fd.write("   store              Take the store action\n")
    fd.write("   purge              Take the purge action\n")
    fd.write('   rebuild            Rebuild "this week\'s" disc if possible\n')
    fd.write("   validate           Validate configuration only\n")
    fd.write("   initialize         Initialize media for use with Cedar Backup\n")
    fd.write("\n")
    fd.write(" You may also specify extended actions that have been defined in\n")
    fd.write(" configuration.\n")
    fd.write("\n")
    fd.write(" You must specify at least one action to take.  More than one of\n")
    fd.write(' the "collect", "stage", "store" or "purge" actions and/or\n')
    fd.write(" extended actions may be specified in any arbitrary order; they\n")
    fd.write(' will be executed in a sensible order.  The "all", "rebuild",\n')
    fd.write(' "validate", and "initialize" actions may not be combined with\n')
    fd.write(" other actions.\n")
    fd.write("\n")


######################
# _version() function
######################


def _version(fd=sys.stdout):
    """
    Prints version information for the cback3 script.
    Args:
       fd: File descriptor used to print information
    *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
    """
    fd.write("\n")
    fd.write(" Cedar Backup version %s, released %s.\n" % (VERSION, DATE))
    fd.write("\n")
    fd.write(" Copyright (c) %s %s <%s>.\n" % (COPYRIGHT, AUTHOR, EMAIL))
    fd.write(" See CREDITS for a list of included code and other contributors.\n")
    fd.write(" This is free software; there is NO warranty.  See the\n")
    fd.write(" GNU General Public License version 2 for copying conditions.\n")
    fd.write("\n")
    fd.write(" Use the --help option for usage information.\n")
    fd.write("\n")


##########################
# _diagnostics() function
##########################


def _diagnostics(fd=sys.stdout):
    """
    Prints runtime diagnostics information.
    Args:
       fd: File descriptor used to print information
    *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
    """
    fd.write("\n")
    fd.write("Diagnostics:\n")
    fd.write("\n")
    Diagnostics().printDiagnostics(fd=fd, prefix="   ")
    fd.write("\n")


##########################
# setupLogging() function
##########################


def setupLogging(options):
    """
    Set up logging based on command-line options.

    There are two kinds of logging: flow logging and output logging.  Output
    logging contains information about system commands executed by Cedar Backup,
    for instance the calls to ``mkisofs`` or ``mount``, etc.  Flow logging
    contains error and informational messages used to understand program flow.
    Flow log messages and output log messages are written to two different
    loggers target (``CedarBackup3.log`` and ``CedarBackup3.output``).  Flow log
    messages are written at the ERROR, INFO and DEBUG log levels, while output
    log messages are generally only written at the INFO log level.

    By default, output logging is disabled.  When the ``options.output`` or
    ``options.debug`` flags are set, output logging will be written to the
    configured logfile.  Output logging is never written to the screen.

    By default, flow logging is enabled at the ERROR level to the screen and at
    the INFO level to the configured logfile.  If the ``options.quiet`` flag is
    set, flow logging is enabled at the INFO level to the configured logfile
    only (i.e. no output will be sent to the screen).  If the ``options.verbose``
    flag is set, flow logging is enabled at the INFO level to both the screen
    and the configured logfile.  If the ``options.debug`` flag is set, flow
    logging is enabled at the DEBUG level to both the screen and the configured
    logfile.

    Args:
       options (:any:`Options` object): Command-line options
    Returns:
        Path to logfile on disk
    """
    logfile = _setupLogfile(options)
    _setupFlowLogging(logfile, options)
    _setupOutputLogging(logfile, options)
    return logfile


def _setupLogfile(options):
    """
    Sets up and creates logfile as needed.

    If the logfile already exists on disk, it will be left as-is, under the
    assumption that it was created with appropriate ownership and permissions.
    If the logfile does not exist on disk, it will be created as an empty file.
    Ownership and permissions will remain at their defaults unless user/group
    and/or mode are set in the options.  We ignore errors setting the indicated
    user and group.

    *Note:* This function is vulnerable to a race condition.  If the log file
    does not exist when the function is run, it will attempt to create the file
    as safely as possible (using ``O_CREAT``).  If two processes attempt to
    create the file at the same time, then one of them will fail.  In practice,
    this shouldn't really be a problem, but it might happen occassionally if two
    instances of cback3 run concurrently or if cback3 collides with logrotate or
    something.

    Args:
       options: Command-line options

    Returns:
        Path to logfile on disk
    """
    if options.logfile is None:
        logfile = DEFAULT_LOGFILE
    else:
        logfile = options.logfile
    if not os.path.exists(logfile):
        mode = DEFAULT_MODE if options.mode is None else options.mode
        orig = os.umask(0)  # Per os.open(), "When computing mode, the current umask value is first masked out"
        try:
            fd = os.open(logfile, os.O_RDWR | os.O_CREAT | os.O_APPEND, mode)
            with os.fdopen(fd, "a+") as f:
                f.write("")
        finally:
            os.umask(orig)
        try:
            if options.owner is None or len(options.owner) < 2:
                (uid, gid) = getUidGid(DEFAULT_OWNERSHIP[0], DEFAULT_OWNERSHIP[1])
            else:
                (uid, gid) = getUidGid(options.owner[0], options.owner[1])
            if sys.platform != "win32":
                os.chown(logfile, uid, gid)  # pylint: disable=no-member
        except:
            pass
    return logfile


def _setupFlowLogging(logfile, options):
    """
    Sets up flow logging.
    Args:
       logfile: Path to logfile on disk
       options: Command-line options
    """
    flowLogger = logging.getLogger("CedarBackup3.log")
    flowLogger.setLevel(logging.DEBUG)  # let the logger see all messages
    _setupDiskFlowLogging(flowLogger, logfile, options)
    _setupScreenFlowLogging(flowLogger, options)


def _setupOutputLogging(logfile, options):
    """
    Sets up command output logging.
    Args:
       logfile: Path to logfile on disk
       options: Command-line options
    """
    outputLogger = logging.getLogger("CedarBackup3.output")
    outputLogger.setLevel(logging.DEBUG)  # let the logger see all messages
    _setupDiskOutputLogging(outputLogger, logfile, options)


def _setupDiskFlowLogging(flowLogger, logfile, options):
    """
    Sets up on-disk flow logging.
    Args:
       flowLogger: Python flow logger object
       logfile: Path to logfile on disk
       options: Command-line options
    """
    formatter = logging.Formatter(fmt=DISK_LOG_FORMAT, datefmt=DATE_FORMAT)
    handler = logging.FileHandler(logfile, mode="a", encoding="utf-8")
    handler.setFormatter(formatter)
    if options.debug:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
    flowLogger.addHandler(handler)


def _setupScreenFlowLogging(flowLogger, options):
    """
    Sets up on-screen flow logging.
    Args:
       flowLogger: Python flow logger object
       options: Command-line options
    """
    formatter = logging.Formatter(fmt=SCREEN_LOG_FORMAT)
    handler = logging.StreamHandler(SCREEN_LOG_STREAM)
    handler.setFormatter(formatter)
    if options.quiet:
        handler.setLevel(logging.CRITICAL)  # effectively turn it off
    elif options.verbose:
        if options.debug:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.ERROR)
    flowLogger.addHandler(handler)


def _setupDiskOutputLogging(outputLogger, logfile, options):
    """
    Sets up on-disk command output logging.
    Args:
       outputLogger: Python command output logger object
       logfile: Path to logfile on disk
       options: Command-line options
    """
    formatter = logging.Formatter(fmt=DISK_OUTPUT_FORMAT, datefmt=DATE_FORMAT)
    handler = logging.FileHandler(logfile, mode="a", encoding="utf-8")
    handler.setFormatter(formatter)
    if options.debug or options.output:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.CRITICAL)  # effectively turn it off
    outputLogger.addHandler(handler)


###############################
# setupPathResolver() function
###############################


def setupPathResolver(config):
    """
    Set up the path resolver singleton based on configuration.

    Cedar Backup's path resolver is implemented in terms of a singleton, the
    :any:`PathResolverSingleton` class.  This function takes options configuration,
    converts it into the dictionary form needed by the singleton, and then
    initializes the singleton.  After that, any function that needs to resolve
    the path of a command can use the singleton.

    Args:
       config (:any:`Config` object): Configuration

    """
    mapping = {}
    if config.options.overrides is not None:
        for override in config.options.overrides:
            mapping[override.command] = override.absolutePath
    singleton = PathResolverSingleton()
    singleton.fill(mapping)


#########################################################################
# Options class definition
########################################################################


@total_ordering
class Options(object):

    ######################
    # Class documentation
    ######################

    """
    Class representing command-line options for the cback3 script.

    The ``Options`` class is a Python object representation of the command-line
    options of the cback3 script.

    The object representation is two-way: a command line string or a list of
    command line arguments can be used to create an ``Options`` object, and then
    changes to the object can be propogated back to a list of command-line
    arguments or to a command-line string.  An ``Options`` object can even be
    created from scratch programmatically (if you have a need for that).

    There are two main levels of validation in the ``Options`` class.  The first
    is field-level validation.  Field-level validation comes into play when a
    given field in an object is assigned to or updated.  We use Python's
    ``property`` functionality to enforce specific validations on field values,
    and in some places we even use customized list classes to enforce
    validations on list members.  You should expect to catch a ``ValueError``
    exception when making assignments to fields if you are programmatically
    filling an object.

    The second level of validation is post-completion validation.  Certain
    validations don't make sense until an object representation of options is
    fully "complete".  We don't want these validations to apply all of the time,
    because it would make building up a valid object from scratch a real pain.
    For instance, we might have to do things in the right order to keep from
    throwing exceptions, etc.

    All of these post-completion validations are encapsulated in the
    :any:`Options.validate` method.  This method can be called at any time by a
    client, and will always be called immediately after creating a ``Options``
    object from a command line and before exporting a ``Options`` object back to
    a command line.  This way, we get acceptable ease-of-use but we also don't
    accept or emit invalid command lines.

    *Note:* Lists within this class are "unordered" for equality comparisons.

    """

    ##############
    # Constructor
    ##############

    def __init__(self, argumentList=None, argumentString=None, validate=True):
        """
        Initializes an options object.

        If you initialize the object without passing either ``argumentList`` or
        ``argumentString``, the object will be empty and will be invalid until it
        is filled in properly.

        No reference to the original arguments is saved off by this class.  Once
        the data has been parsed (successfully or not) this original information
        is discarded.

        The argument list is assumed to be a list of arguments, not including the
        name of the command, something like ``sys.argv[1:]``.  If you pass
        ``sys.argv`` instead, things are not going to work.

        The argument string will be parsed into an argument list by the
        :any:`util.splitCommandLine` function (see the documentation for that
        function for some important notes about its limitations).  There is an
        assumption that the resulting list will be equivalent to ``sys.argv[1:]``,
        just like ``argumentList``.

        Unless the ``validate`` argument is ``False``, the :any:`Options.validate`
        method will be called (with its default arguments) after successfully
        parsing any passed-in command line.  This validation ensures that
        appropriate actions, etc. have been specified.  Keep in mind that even if
        ``validate`` is ``False``, it might not be possible to parse the passed-in
        command line, so an exception might still be raised.

        *Note:* The command line format is specified by the ``_usage`` function.
        Call ``_usage`` to see a usage statement for the cback3 script.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to read in
        invalid command line arguments.

        Args:
           argumentList (List of arguments, i.e. ``sys.argv``): Command line for a program
           argumentString (String, i.e. "cback3 --verbose stage store"): Command line for a program
           validate (Boolean true/false): Validate the command line after parsing it
        Raises:
           getopt.GetoptError: If the command-line arguments could not be parsed
           ValueError: If the command-line arguments are invalid
        """
        self._help = False
        self._version = False
        self._verbose = False
        self._quiet = False
        self._config = None
        self._full = False
        self._managed = False
        self._managedOnly = False
        self._logfile = None
        self._owner = None
        self._mode = None
        self._output = False
        self._debug = False
        self._stacktrace = False
        self._diagnostics = False
        self._actions = None
        self.actions = []  # initialize to an empty list; remainder are OK
        if argumentList is not None and argumentString is not None:
            raise ValueError("Use either argumentList or argumentString, but not both.")
        if argumentString is not None:
            argumentList = splitCommandLine(argumentString)
        if argumentList is not None:
            self._parseArgumentList(argumentList)
            if validate:
                self.validate()

    #########################
    # String representations
    #########################

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return self.buildArgumentString(validate=False)

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    #############################
    # Standard comparison method
    #############################

    def __eq__(self, other):
        """Equals operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        """Less-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        """Greater-than operator, implemented in terms of original Python 2 compare operator."""
        return self.__cmp__(other) > 0

    def __cmp__(self, other):
        """
        Original Python 2 comparison operator.
        Lists within this class are "unordered" for equality comparisons.
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        if other is None:
            return 1
        if self.help != other.help:
            if self.help < other.help:
                return -1
            else:
                return 1
        if self.version != other.version:
            if self.version < other.version:
                return -1
            else:
                return 1
        if self.verbose != other.verbose:
            if self.verbose < other.verbose:
                return -1
            else:
                return 1
        if self.quiet != other.quiet:
            if self.quiet < other.quiet:
                return -1
            else:
                return 1
        if self.config != other.config:
            if self.config < other.config:
                return -1
            else:
                return 1
        if self.full != other.full:
            if self.full < other.full:
                return -1
            else:
                return 1
        if self.managed != other.managed:
            if self.managed < other.managed:
                return -1
            else:
                return 1
        if self.managedOnly != other.managedOnly:
            if self.managedOnly < other.managedOnly:
                return -1
            else:
                return 1
        if self.logfile != other.logfile:
            if str(self.logfile or "") < str(other.logfile or ""):
                return -1
            else:
                return 1
        if self.owner != other.owner:
            if str(self.owner or "") < str(other.owner or ""):
                return -1
            else:
                return 1
        if self.mode != other.mode:
            if int(self.mode or 0) < int(other.mode or 0):
                return -1
            else:
                return 1
        if self.output != other.output:
            if self.output < other.output:
                return -1
            else:
                return 1
        if self.debug != other.debug:
            if self.debug < other.debug:
                return -1
            else:
                return 1
        if self.stacktrace != other.stacktrace:
            if self.stacktrace < other.stacktrace:
                return -1
            else:
                return 1
        if self.diagnostics != other.diagnostics:
            if self.diagnostics < other.diagnostics:
                return -1
            else:
                return 1
        if self.actions != other.actions:
            if self.actions < other.actions:
                return -1
            else:
                return 1
        return 0

    #############
    # Properties
    #############

    def _setHelp(self, value):
        """
        Property target used to set the help flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._help = True
        else:
            self._help = False

    def _getHelp(self):
        """
        Property target used to get the help flag.
        """
        return self._help

    def _setVersion(self, value):
        """
        Property target used to set the version flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._version = True
        else:
            self._version = False

    def _getVersion(self):
        """
        Property target used to get the version flag.
        """
        return self._version

    def _setVerbose(self, value):
        """
        Property target used to set the verbose flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._verbose = True
        else:
            self._verbose = False

    def _getVerbose(self):
        """
        Property target used to get the verbose flag.
        """
        return self._verbose

    def _setQuiet(self, value):
        """
        Property target used to set the quiet flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._quiet = True
        else:
            self._quiet = False

    def _getQuiet(self):
        """
        Property target used to get the quiet flag.
        """
        return self._quiet

    def _setConfig(self, value):
        """
        Property target used to set the config parameter.
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The config parameter must be a non-empty string.")
        self._config = value

    def _getConfig(self):
        """
        Property target used to get the config parameter.
        """
        return self._config

    def _setFull(self, value):
        """
        Property target used to set the full flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._full = True
        else:
            self._full = False

    def _getFull(self):
        """
        Property target used to get the full flag.
        """
        return self._full

    def _setManaged(self, value):
        """
        Property target used to set the managed flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._managed = True
        else:
            self._managed = False

    def _getManaged(self):
        """
        Property target used to get the managed flag.
        """
        return self._managed

    def _setManagedOnly(self, value):
        """
        Property target used to set the managedOnly flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._managedOnly = True
        else:
            self._managedOnly = False

    def _getManagedOnly(self):
        """
        Property target used to get the managedOnly flag.
        """
        return self._managedOnly

    def _setLogfile(self, value):
        """
        Property target used to set the logfile parameter.
        Raises:
           ValueError: If the value cannot be encoded properly
        """
        if value is not None:
            if len(value) < 1:
                raise ValueError("The logfile parameter must be a non-empty string.")
        self._logfile = encodePath(value)

    def _getLogfile(self):
        """
        Property target used to get the logfile parameter.
        """
        return self._logfile

    def _setOwner(self, value):
        """
        Property target used to set the owner parameter.
        If not ``None``, the owner must be a ``(user,group)`` tuple or list.
        Strings (and inherited children of strings) are explicitly disallowed.
        The value will be normalized to a tuple.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._owner = None
        else:
            if isinstance(value, str):
                raise ValueError("Must specify user and group tuple for owner parameter.")
            if len(value) != 2:
                raise ValueError("Must specify user and group tuple for owner parameter.")
            if len(value[0]) < 1 or len(value[1]) < 1:
                raise ValueError("User and group tuple values must be non-empty strings.")
            self._owner = (value[0], value[1])

    def _getOwner(self):
        """
        Property target used to get the owner parameter.
        The parameter is a tuple of ``(user, group)``.
        """
        return self._owner

    def _setMode(self, value):
        """
        Property target used to set the mode parameter.
        """
        if value is None:
            self._mode = None
        else:
            try:
                if isinstance(value, str):
                    value = int(value, 8)
                else:
                    value = int(value)
            except TypeError:
                raise ValueError("Mode must be an octal integer >= 0, i.e. 644.")
            if value < 0:
                raise ValueError("Mode must be an octal integer >= 0. i.e. 644.")
            self._mode = value

    def _getMode(self):
        """
        Property target used to get the mode parameter.
        """
        return self._mode

    def _setOutput(self, value):
        """
        Property target used to set the output flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._output = True
        else:
            self._output = False

    def _getOutput(self):
        """
        Property target used to get the output flag.
        """
        return self._output

    def _setDebug(self, value):
        """
        Property target used to set the debug flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._debug = True
        else:
            self._debug = False

    def _getDebug(self):
        """
        Property target used to get the debug flag.
        """
        return self._debug

    def _setStacktrace(self, value):
        """
        Property target used to set the stacktrace flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._stacktrace = True
        else:
            self._stacktrace = False

    def _getStacktrace(self):
        """
        Property target used to get the stacktrace flag.
        """
        return self._stacktrace

    def _setDiagnostics(self, value):
        """
        Property target used to set the diagnostics flag.
        No validations, but we normalize the value to ``True`` or ``False``.
        """
        if value:
            self._diagnostics = True
        else:
            self._diagnostics = False

    def _getDiagnostics(self):
        """
        Property target used to get the diagnostics flag.
        """
        return self._diagnostics

    def _setActions(self, value):
        """
        Property target used to set the actions list.
        We don't restrict the contents of actions.  They're validated somewhere else.
        Raises:
           ValueError: If the value is not valid
        """
        if value is None:
            self._actions = None
        else:
            try:
                saved = self._actions
                self._actions = []
                self._actions.extend(value)
            except Exception as e:
                self._actions = saved
                raise e

    def _getActions(self):
        """
        Property target used to get the actions list.
        """
        return self._actions

    help = property(_getHelp, _setHelp, None, "Command-line help (``-h,--help``) flag.")
    version = property(_getVersion, _setVersion, None, "Command-line version (``-V,--version``) flag.")
    verbose = property(_getVerbose, _setVerbose, None, "Command-line verbose (``-b,--verbose``) flag.")
    quiet = property(_getQuiet, _setQuiet, None, "Command-line quiet (``-q,--quiet``) flag.")
    config = property(_getConfig, _setConfig, None, "Command-line configuration file (``-c,--config``) parameter.")
    full = property(_getFull, _setFull, None, "Command-line full-backup (``-f,--full``) flag.")
    managed = property(_getManaged, _setManaged, None, "Command-line managed (``-M,--managed``) flag.")
    managedOnly = property(_getManagedOnly, _setManagedOnly, None, "Command-line managed-only (``-N,--managed-only``) flag.")
    logfile = property(_getLogfile, _setLogfile, None, "Command-line logfile (``-l,--logfile``) parameter.")
    owner = property(_getOwner, _setOwner, None, "Command-line owner (``-o,--owner``) parameter, as tuple ``(user,group)``.")
    mode = property(_getMode, _setMode, None, "Command-line mode (``-m,--mode``) parameter.")
    output = property(_getOutput, _setOutput, None, "Command-line output (``-O,--output``) flag.")
    debug = property(_getDebug, _setDebug, None, "Command-line debug (``-d,--debug``) flag.")
    stacktrace = property(_getStacktrace, _setStacktrace, None, "Command-line stacktrace (``-s,--stack``) flag.")
    diagnostics = property(_getDiagnostics, _setDiagnostics, None, "Command-line diagnostics (``-D,--diagnostics``) flag.")
    actions = property(_getActions, _setActions, None, "Command-line actions list.")

    ##################
    # Utility methods
    ##################

    def validate(self):
        """
        Validates command-line options represented by the object.

        Unless ``--help`` or ``--version`` are supplied, at least one action must
        be specified.  Other validations (as for allowed values for particular
        options) will be taken care of at assignment time by the properties
        functionality.

        *Note:* The command line format is specified by the ``_usage`` function.
        Call ``_usage`` to see a usage statement for the cback3 script.

        Raises:
           ValueError: If one of the validations fails
        """
        if not self.help and not self.version and not self.diagnostics:
            if self.actions is None or len(self.actions) == 0:
                raise ValueError("At least one action must be specified.")
        if self.managed and self.managedOnly:
            raise ValueError("The --managed and --managed-only options may not be combined.")

    def buildArgumentList(self, validate=True):
        """
        Extracts options into a list of command line arguments.

        The original order of the various arguments (if, indeed, the object was
        initialized with a command-line) is not preserved in this generated
        argument list.   Besides that, the argument list is normalized to use the
        long option names (i.e. --version rather than -V).  The resulting list
        will be suitable for passing back to the constructor in the
        ``argumentList`` parameter.  Unlike :any:`buildArgumentString`, string
        arguments are not quoted here, because there is no need for it.

        Unless the ``validate`` parameter is ``False``, the :any:`Options.validate`
        method will be called (with its default arguments) against the
        options before extracting the command line.  If the options are not valid,
        then an argument list will not be extracted.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to extract an
        invalid command line.

        Args:
           validate (Boolean true/false): Validate the options before extracting the command line
        Returns:
            List representation of command-line arguments
        Raises:
           ValueError: If options within the object are invalid
        """
        if validate:
            self.validate()
        argumentList = []
        if self._help:
            argumentList.append("--help")
        if self.version:
            argumentList.append("--version")
        if self.verbose:
            argumentList.append("--verbose")
        if self.quiet:
            argumentList.append("--quiet")
        if self.config is not None:
            argumentList.append("--config")
            argumentList.append(self.config)
        if self.full:
            argumentList.append("--full")
        if self.managed:
            argumentList.append("--managed")
        if self.managedOnly:
            argumentList.append("--managed-only")
        if self.logfile is not None:
            argumentList.append("--logfile")
            argumentList.append(self.logfile)
        if self.owner is not None:
            argumentList.append("--owner")
            argumentList.append("%s:%s" % (self.owner[0], self.owner[1]))
        if self.mode is not None:
            argumentList.append("--mode")
            argumentList.append("%o" % self.mode)
        if self.output:
            argumentList.append("--output")
        if self.debug:
            argumentList.append("--debug")
        if self.stacktrace:
            argumentList.append("--stack")
        if self.diagnostics:
            argumentList.append("--diagnostics")
        if self.actions is not None:
            for action in self.actions:
                argumentList.append(action)
        return argumentList

    def buildArgumentString(self, validate=True):
        """
        Extracts options into a string of command-line arguments.

        The original order of the various arguments (if, indeed, the object was
        initialized with a command-line) is not preserved in this generated
        argument string.   Besides that, the argument string is normalized to use
        the long option names (i.e. --version rather than -V) and to quote all
        string arguments with double quotes (``"``).  The resulting string will be
        suitable for passing back to the constructor in the ``argumentString``
        parameter.

        Unless the ``validate`` parameter is ``False``, the :any:`Options.validate`
        method will be called (with its default arguments) against the options
        before extracting the command line.  If the options are not valid, then
        an argument string will not be extracted.

        *Note:* It is strongly suggested that the ``validate`` option always be set
        to ``True`` (the default) unless there is a specific need to extract an
        invalid command line.

        Args:
           validate (Boolean true/false): Validate the options before extracting the command line
        Returns:
            String representation of command-line arguments
        Raises:
           ValueError: If options within the object are invalid
        """
        if validate:
            self.validate()
        argumentString = ""
        if self._help:
            argumentString += "--help "
        if self.version:
            argumentString += "--version "
        if self.verbose:
            argumentString += "--verbose "
        if self.quiet:
            argumentString += "--quiet "
        if self.config is not None:
            argumentString += '--config "%s" ' % self.config
        if self.full:
            argumentString += "--full "
        if self.managed:
            argumentString += "--managed "
        if self.managedOnly:
            argumentString += "--managed-only "
        if self.logfile is not None:
            argumentString += '--logfile "%s" ' % self.logfile
        if self.owner is not None:
            argumentString += '--owner "%s:%s" ' % (self.owner[0], self.owner[1])
        if self.mode is not None:
            argumentString += "--mode %o " % self.mode
        if self.output:
            argumentString += "--output "
        if self.debug:
            argumentString += "--debug "
        if self.stacktrace:
            argumentString += "--stack "
        if self.diagnostics:
            argumentString += "--diagnostics "
        if self.actions is not None:
            for action in self.actions:
                argumentString += '"%s" ' % action
        return argumentString

    def _parseArgumentList(self, argumentList):
        """
        Internal method to parse a list of command-line arguments.

        Most of the validation we do here has to do with whether the arguments
        can be parsed and whether any values which exist are valid.  We don't do
        any validation as to whether required elements exist or whether elements
        exist in the proper combination (instead, that's the job of the
        :any:`validate` method).

        For any of the options which supply parameters, if the option is
        duplicated with long and short switches (i.e. ``-l`` and a ``--logfile``)
        then the long switch is used.  If the same option is duplicated with the
        same switch (long or short), then the last entry on the command line is
        used.

        Args:
           argumentList (List of arguments to a command, i.e. ``sys.argv[1:]``): List of arguments to a command
        Raises:
           ValueError: If the argument list cannot be successfully parsed
        """
        switches = {}
        opts, self.actions = getopt.getopt(argumentList, SHORT_SWITCHES, LONG_SWITCHES)
        for o, a in opts:  # push the switches into a hash
            switches[o] = a
        if "-h" in switches or "--help" in switches:
            self.help = True
        if "-V" in switches or "--version" in switches:
            self.version = True
        if "-b" in switches or "--verbose" in switches:
            self.verbose = True
        if "-q" in switches or "--quiet" in switches:
            self.quiet = True
        if "-c" in switches:
            self.config = switches["-c"]
        if "--config" in switches:
            self.config = switches["--config"]
        if "-f" in switches or "--full" in switches:
            self.full = True
        if "-M" in switches or "--managed" in switches:
            self.managed = True
        if "-N" in switches or "--managed-only" in switches:
            self.managedOnly = True
        if "-l" in switches:
            self.logfile = switches["-l"]
        if "--logfile" in switches:
            self.logfile = switches["--logfile"]
        if "-o" in switches:
            self.owner = switches["-o"].split(":", 1)
        if "--owner" in switches:
            self.owner = switches["--owner"].split(":", 1)
        if "-m" in switches:
            self.mode = switches["-m"]
        if "--mode" in switches:
            self.mode = switches["--mode"]
        if "-O" in switches or "--output" in switches:
            self.output = True
        if "-d" in switches or "--debug" in switches:
            self.debug = True
        if "-s" in switches or "--stack" in switches:
            self.stacktrace = True
        if "-D" in switches or "--diagnostics" in switches:
            self.diagnostics = True


#########################################################################
# Main routine
########################################################################

if __name__ == "__main__":
    result = cli()
    sys.exit(result)
