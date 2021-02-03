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
# Copyright (c) 2004-2008,2010,2015 Kenneth J. Pronovici.
# All rights reserved.
#
# Portions copyright (c) 2001, 2002 Python Software Foundation.
# All Rights Reserved.
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
# Purpose  : Provides general-purpose utilities.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides general-purpose utilities.

Module Attributes
=================

Attributes:
   ISO_SECTOR_SIZE: Size of an ISO image sector, in bytes
   BYTES_PER_SECTOR: Number of bytes (B) per ISO sector
   BYTES_PER_KBYTE: Number of bytes (B) per kilobyte (kB)
   BYTES_PER_MBYTE: Number of bytes (B) per megabyte (MB)
   BYTES_PER_GBYTE: Number of bytes (B) per megabyte (GB)
   KBYTES_PER_MBYTE: Number of kilobytes (kB) per megabyte (MB)
   MBYTES_PER_GBYTE: Number of megabytes (MB) per gigabyte (GB)
   SECONDS_PER_MINUTE: Number of seconds per minute
   MINUTES_PER_HOUR: Number of minutes per hour
   HOURS_PER_DAY: Number of hours per day
   SECONDS_PER_DAY: Number of seconds per day
   UNIT_BYTES: Constant representing the byte (B) unit for conversion
   UNIT_KBYTES: Constant representing the kilobyte (kB) unit for conversion
   UNIT_MBYTES: Constant representing the megabyte (MB) unit for conversion
   UNIT_GBYTES: Constant representing the gigabyte (GB) unit for conversion
   UNIT_SECTORS: Constant representing the ISO sector unit for conversion

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""


########################################################################
# Imported modules
########################################################################

import collections
import logging
import math
import os
import platform
import re
import sys
import time
from decimal import Decimal
from functools import total_ordering
from numbers import Real
from subprocess import PIPE, STDOUT, Popen

from CedarBackup3.release import DATE, VERSION

try:
    import grp
    import pwd

    _UID_GID_AVAILABLE = True
except ImportError:
    _UID_GID_AVAILABLE = False


########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.util")
outputLogger = logging.getLogger("CedarBackup3.output")

ISO_SECTOR_SIZE = 2048.0  # in bytes
BYTES_PER_SECTOR = ISO_SECTOR_SIZE

BYTES_PER_KBYTE = 1024.0
KBYTES_PER_MBYTE = 1024.0
MBYTES_PER_GBYTE = 1024.0
BYTES_PER_MBYTE = BYTES_PER_KBYTE * KBYTES_PER_MBYTE
BYTES_PER_GBYTE = BYTES_PER_MBYTE * MBYTES_PER_GBYTE

SECONDS_PER_MINUTE = 60.0
MINUTES_PER_HOUR = 60.0
HOURS_PER_DAY = 24.0
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY

UNIT_BYTES = 0
UNIT_KBYTES = 1
UNIT_MBYTES = 2
UNIT_GBYTES = 4
UNIT_SECTORS = 3

MTAB_FILE = "/etc/mtab"

MOUNT_COMMAND = ["mount"]
UMOUNT_COMMAND = ["umount"]

DEFAULT_LANGUAGE = "C"
LANG_VAR = "LANG"
LOCALE_VARS = [
    "LC_ADDRESS",
    "LC_ALL",
    "LC_COLLATE",
    "LC_CTYPE",
    "LC_IDENTIFICATION",
    "LC_MEASUREMENT",
    "LC_MESSAGES",
    "LC_MONETARY",
    "LC_NAME",
    "LC_NUMERIC",
    "LC_PAPER",
    "LC_TELEPHONE",
    "LC_TIME",
]


########################################################################
# UnorderedList class definition
########################################################################


class UnorderedList(list):

    """
    Class representing an "unordered list".

    An "unordered list" is a list in which only the contents matter, not the
    order in which the contents appear in the list.

    For instance, we might be keeping track of set of paths in a list, because
    it's convenient to have them in that form.  However, for comparison
    purposes, we would only care that the lists contain exactly the same
    contents, regardless of order.

    I have come up with two reasonable ways of doing this, plus a couple more
    that would work but would be a pain to implement.  My first method is to
    copy and sort each list, comparing the sorted versions.  This will only work
    if two lists with exactly the same members are guaranteed to sort in exactly
    the same order.  The second way would be to create two Sets and then compare
    the sets.  However, this would lose information about any duplicates in
    either list.  I've decided to go with option #1 for now.  I'll modify this
    code if I run into problems in the future.

    We override the original ``__eq__``, ``__ne__``, ``__ge__``, ``__gt__``,
    ``__le__`` and ``__lt__`` list methods to change the definition of the various
    comparison operators.  In all cases, the comparison is changed to return the
    result of the original operation *but instead comparing sorted lists*.
    This is going to be quite a bit slower than a normal list, so you probably
    only want to use it on small lists.
    """

    def __eq__(self, other):
        """
        Definition of ``==`` operator for this class.
        Args:
           other: Other object to compare to
        Returns:
            True/false depending on whether ``self == other``
        """
        if other is None:
            return False
        selfSorted = UnorderedList.mixedsort(self[:])
        otherSorted = UnorderedList.mixedsort(other[:])
        return selfSorted.__eq__(otherSorted)

    def __ne__(self, other):
        """
        Definition of ``!=`` operator for this class.
        Args:
           other: Other object to compare to
        Returns:
            True/false depending on whether ``self != other``
        """
        if other is None:
            return True
        selfSorted = UnorderedList.mixedsort(self[:])
        otherSorted = UnorderedList.mixedsort(other[:])
        return selfSorted.__ne__(otherSorted)

    def __ge__(self, other):
        """
        Definition of S{>=} operator for this class.
        Args:
           other: Other object to compare to
        Returns:
            True/false depending on whether ``self >= other``
        """
        if other is None:
            return True
        selfSorted = UnorderedList.mixedsort(self[:])
        otherSorted = UnorderedList.mixedsort(other[:])
        return selfSorted.__ge__(otherSorted)

    def __gt__(self, other):
        """
        Definition of ``>`` operator for this class.
        Args:
           other: Other object to compare to
        Returns:
            True/false depending on whether ``self > other``
        """
        if other is None:
            return True
        selfSorted = UnorderedList.mixedsort(self[:])
        otherSorted = UnorderedList.mixedsort(other[:])
        return selfSorted.__gt__(otherSorted)

    def __le__(self, other):
        """
        Definition of S{<=} operator for this class.
        Args:
           other: Other object to compare to
        Returns:
            True/false depending on whether ``self <= other``
        """
        if other is None:
            return False
        selfSorted = UnorderedList.mixedsort(self[:])
        otherSorted = UnorderedList.mixedsort(other[:])
        return selfSorted.__le__(otherSorted)

    def __lt__(self, other):
        """
        Definition of ``<`` operator for this class.
        Args:
           other: Other object to compare to
        Returns:
            True/false depending on whether ``self < other``
        """
        if other is None:
            return False
        selfSorted = UnorderedList.mixedsort(self[:])
        otherSorted = UnorderedList.mixedsort(other[:])
        return selfSorted.__lt__(otherSorted)

    @staticmethod
    def mixedsort(value):
        """
        Sort a list, making sure we don't blow up if the list happens to include mixed values.
        @see: http://stackoverflow.com/questions/26575183/how-can-i-get-2-x-like-sorting-behaviour-in-python-3-x
        """
        return sorted(value, key=UnorderedList.mixedkey)

    @staticmethod
    def mixedkey(value):
        """Provide a key for use by mixedsort()"""
        numeric = Real, Decimal
        if isinstance(value, numeric):
            typeinfo = numeric
        else:
            typeinfo = type(value)
        try:
            # pylint: disable=R0124
            x = value < value
        except TypeError:
            value = repr(value)
        return repr(typeinfo), value


########################################################################
# AbsolutePathList class definition
########################################################################


class AbsolutePathList(UnorderedList):

    """
    Class representing a list of absolute paths.

    This is an unordered list.

    We override the ``append``, ``insert`` and ``extend`` methods to ensure that
    any item added to the list is an absolute path.

    Each item added to the list is encoded using :any:`encodePath`.  If we don't do
    this, we have problems trying certain operations between strings and unicode
    objects, particularly for "odd" filenames that can't be encoded in standard
    ASCII.
    """

    def append(self, item):
        """
        Overrides the standard ``append`` method.
        Raises:
           ValueError: If item is not an absolute path
        """
        if not os.path.isabs(item):
            raise ValueError("Not an absolute path: [%s]" % item)
        list.append(self, encodePath(item))

    def insert(self, index, item):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If item is not an absolute path
        """
        if not os.path.isabs(item):
            raise ValueError("Not an absolute path: [%s]" % item)
        list.insert(self, index, encodePath(item))

    def extend(self, seq):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If any item is not an absolute path
        """
        for item in seq:
            if not os.path.isabs(item):
                raise ValueError("Not an absolute path: [%s]" % item)
        for item in seq:
            list.append(self, encodePath(item))


########################################################################
# ObjectTypeList class definition
########################################################################


class ObjectTypeList(UnorderedList):

    """
    Class representing a list containing only objects with a certain type.

    This is an unordered list.

    We override the ``append``, ``insert`` and ``extend`` methods to ensure that
    any item added to the list matches the type that is requested.  The
    comparison uses the built-in ``isinstance``, which should allow subclasses of
    of the requested type to be added to the list as well.

    The ``objectName`` value will be used in exceptions, i.e. C{"Item must be a
    CollectDir object."} if ``objectName`` is ``"CollectDir"``.
    """

    def __init__(self, objectType, objectName):
        """
        Initializes a typed list for a particular type.
        Args:
           objectType: Type that the list elements must match
           objectName: Short string containing the "name" of the type
        """
        super(ObjectTypeList, self).__init__()
        self.objectType = objectType
        self.objectName = objectName

    def append(self, item):
        """
        Overrides the standard ``append`` method.
        Raises:
           ValueError: If item does not match requested type
        """
        if not isinstance(item, self.objectType):
            raise ValueError("Item must be a %s object." % self.objectName)
        list.append(self, item)

    def insert(self, index, item):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If item does not match requested type
        """
        if not isinstance(item, self.objectType):
            raise ValueError("Item must be a %s object." % self.objectName)
        list.insert(self, index, item)

    def extend(self, seq):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If item does not match requested type
        """
        for item in seq:
            if not isinstance(item, self.objectType):
                raise ValueError("All items must be %s objects." % self.objectName)
        list.extend(self, seq)


########################################################################
# RestrictedContentList class definition
########################################################################


class RestrictedContentList(UnorderedList):

    """
    Class representing a list containing only object with certain values.

    This is an unordered list.

    We override the ``append``, ``insert`` and ``extend`` methods to ensure that
    any item added to the list is among the valid values.  We use a standard
    comparison, so pretty much anything can be in the list of valid values.

    The ``valuesDescr`` value will be used in exceptions, i.e. C{"Item must be
    one of values in VALID_ACTIONS"} if ``valuesDescr`` is ``"VALID_ACTIONS"``.

    *Note:*  This class doesn't make any attempt to trap for nonsensical
    arguments.  All of the values in the values list should be of the same type
    (i.e. strings).  Then, all list operations also need to be of that type
    (i.e. you should always insert or append just strings).  If you mix types --
    for instance lists and strings -- you will likely see AttributeError
    exceptions or other problems.
    """

    def __init__(self, valuesList, valuesDescr, prefix=None):
        """
        Initializes a list restricted to containing certain values.
        Args:
           valuesList: List of valid values
           valuesDescr: Short string describing list of values
           prefix: Prefix to use in error messages (None results in prefix "Item")
        """
        super(RestrictedContentList, self).__init__()
        self.prefix = "Item"
        if prefix is not None:
            self.prefix = prefix
        self.valuesList = valuesList
        self.valuesDescr = valuesDescr

    def append(self, item):
        """
        Overrides the standard ``append`` method.
        Raises:
           ValueError: If item is not in the values list
        """
        if item not in self.valuesList:
            raise ValueError("%s must be one of the values in %s." % (self.prefix, self.valuesDescr))
        list.append(self, item)

    def insert(self, index, item):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If item is not in the values list
        """
        if item not in self.valuesList:
            raise ValueError("%s must be one of the values in %s." % (self.prefix, self.valuesDescr))
        list.insert(self, index, item)

    def extend(self, seq):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If item is not in the values list
        """
        for item in seq:
            if item not in self.valuesList:
                raise ValueError("%s must be one of the values in %s." % (self.prefix, self.valuesDescr))
        list.extend(self, seq)


########################################################################
# RegexMatchList class definition
########################################################################


class RegexMatchList(UnorderedList):

    """
    Class representing a list containing only strings that match a regular expression.

    If ``emptyAllowed`` is passed in as ``False``, then empty strings are
    explicitly disallowed, even if they happen to match the regular expression.
    (``None`` values are always disallowed, since string operations are not
    permitted on ``None``.)

    This is an unordered list.

    We override the ``append``, ``insert`` and ``extend`` methods to ensure that
    any item added to the list matches the indicated regular expression.

    *Note:* If you try to put values that are not strings into the list, you will
    likely get either TypeError or AttributeError exceptions as a result.
    """

    def __init__(self, valuesRegex, emptyAllowed=True, prefix=None):
        """
        Initializes a list restricted to containing certain values.
        Args:
           valuesRegex: Regular expression that must be matched, as a string
           emptyAllowed: Indicates whether empty or None values are allowed
           prefix: Prefix to use in error messages (None results in prefix "Item")
        """
        super(RegexMatchList, self).__init__()
        self.prefix = "Item"
        if prefix is not None:
            self.prefix = prefix
        self.valuesRegex = valuesRegex
        self.emptyAllowed = emptyAllowed
        self.pattern = re.compile(self.valuesRegex)

    def append(self, item):
        """
        Overrides the standard ``append`` method.

        Raises:
           ValueError: If item is None
           ValueError: If item is empty and empty values are not allowed
           ValueError: If item does not match the configured regular expression
        """
        if item is None or (not self.emptyAllowed and item == ""):
            raise ValueError("%s cannot be empty." % self.prefix)
        if not self.pattern.search(item):
            raise ValueError("%s is not valid: [%s]" % (self.prefix, item))
        list.append(self, item)

    def insert(self, index, item):
        """
        Overrides the standard ``insert`` method.

        Raises:
           ValueError: If item is None
           ValueError: If item is empty and empty values are not allowed
           ValueError: If item does not match the configured regular expression
        """
        if item is None or (not self.emptyAllowed and item == ""):
            raise ValueError("%s cannot be empty." % self.prefix)
        if not self.pattern.search(item):
            raise ValueError("%s is not valid [%s]" % (self.prefix, item))
        list.insert(self, index, item)

    def extend(self, seq):
        """
        Overrides the standard ``insert`` method.

        Raises:
           ValueError: If any item is None
           ValueError: If any item is empty and empty values are not allowed
           ValueError: If any item does not match the configured regular expression
        """
        for item in seq:
            if item is None or (not self.emptyAllowed and item == ""):
                raise ValueError("%s cannot be empty." % self.prefix)
            if not self.pattern.search(item):
                raise ValueError("%s is not valid: [%s]" % (self.prefix, item))
        list.extend(self, seq)


########################################################################
# RegexList class definition
########################################################################


class RegexList(UnorderedList):

    """
    Class representing a list of valid regular expression strings.

    This is an unordered list.

    We override the ``append``, ``insert`` and ``extend`` methods to ensure that
    any item added to the list is a valid regular expression.
    """

    def append(self, item):
        """
        Overrides the standard ``append`` method.
        Raises:
           ValueError: If item is not an absolute path
        """
        try:
            re.compile(item)
        except re.error:
            raise ValueError("Not a valid regular expression: [%s]" % item)
        list.append(self, item)

    def insert(self, index, item):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If item is not an absolute path
        """
        try:
            re.compile(item)
        except re.error:
            raise ValueError("Not a valid regular expression: [%s]" % item)
        list.insert(self, index, item)

    def extend(self, seq):
        """
        Overrides the standard ``insert`` method.
        Raises:
           ValueError: If any item is not an absolute path
        """
        for item in seq:
            try:
                re.compile(item)
            except re.error:
                raise ValueError("Not a valid regular expression: [%s]" % item)
        for item in seq:
            list.append(self, item)


########################################################################
# Directed graph implementation
########################################################################


class _Vertex(object):

    """
    Represents a vertex (or node) in a directed graph.
    """

    def __init__(self, name):
        """
        Constructor.
        Args:
           name (String value): Name of this graph vertex

        """
        self.name = name
        self.endpoints = []
        self.state = None


@total_ordering
class DirectedGraph(object):

    """
    Represents a directed graph.

    A graph **G=(V,E)** consists of a set of vertices **V** together with a set
    **E** of vertex pairs or edges.  In a directed graph, each edge also has an
    associated direction (from vertext **v1** to vertex **v2**).  A ``DirectedGraph``
    object provides a way to construct a directed graph and execute a depth-
    first search.

    This data structure was designed based on the graphing chapter in
    U{The Algorithm Design Manual<http://www2.toki.or.id/book/AlgDesignManual/>},
    by Steven S. Skiena.

    This class is intended to be used by Cedar Backup for dependency ordering.
    Because of this, it's not quite general-purpose.  Unlike a "general" graph,
    every vertex in this graph has at least one edge pointing to it, from a
    special "start" vertex.  This is so no vertices get "lost" either because
    they have no dependencies or because nothing depends on them.
    """

    _UNDISCOVERED = 0
    _DISCOVERED = 1
    _EXPLORED = 2

    def __init__(self, name):
        """
        Directed graph constructor.

        Args:
           name (String value): Name of this graph

        """
        if name is None or name == "":
            raise ValueError("Graph name must be non-empty.")
        self._name = name
        self._vertices = {}
        self._startVertex = _Vertex(None)  # start vertex is only vertex with no name

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "DirectedGraph(%s)" % self.name

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

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
        Args:
           other: Other object to compare to
        Returns:
            -1/0/1 depending on whether self is ``<``, ``=`` or ``>`` other
        """
        # pylint: disable=W0212
        if other is None:
            return 1
        if self.name != other.name:
            if str(self.name or "") < str(other.name or ""):
                return -1
            else:
                return 1
        if self._vertices != other._vertices:
            if self._vertices < other._vertices:
                return -1
            else:
                return 1
        return 0

    def _getName(self):
        """
        Property target used to get the graph name.
        """
        return self._name

    name = property(_getName, None, None, "Name of the graph.")

    def createVertex(self, name):
        """
        Creates a named vertex.
        Args:
           name: vertex name
        Raises:
           ValueError: If the vertex name is ``None`` or empty
        """
        if name is None or name == "":
            raise ValueError("Vertex name must be non-empty.")
        vertex = _Vertex(name)
        self._startVertex.endpoints.append(vertex)  # so every vertex is connected at least once
        self._vertices[name] = vertex

    def createEdge(self, start, finish):
        """
        Adds an edge with an associated direction, from ``start`` vertex to ``finish`` vertex.
        Args:
           start: Name of start vertex
           finish: Name of finish vertex
        Raises:
           ValueError: If one of the named vertices is unknown
        """
        try:
            startVertex = self._vertices[start]
            finishVertex = self._vertices[finish]
            startVertex.endpoints.append(finishVertex)
        except KeyError as e:
            raise ValueError("Vertex [%s] could not be found." % e)

    def topologicalSort(self):
        """
        Implements a topological sort of the graph.

        This method also enforces that the graph is a directed acyclic graph,
        which is a requirement of a topological sort.

        A directed acyclic graph (or "DAG") is a directed graph with no directed
        cycles.  A topological sort of a DAG is an ordering on the vertices such
        that all edges go from left to right.  Only an acyclic graph can have a
        topological sort, but any DAG has at least one topological sort.

        Since a topological sort only makes sense for an acyclic graph, this
        method throws an exception if a cycle is found.

        A depth-first search only makes sense if the graph is acyclic.  If the
        graph contains any cycles, it is not possible to determine a consistent
        ordering for the vertices.

        *Note:* If a particular vertex has no edges, then its position in the
        final list depends on the order in which the vertices were created in the
        graph.  If you're using this method to determine a dependency order, this
        makes sense: a vertex with no dependencies can go anywhere (and will).

        Returns:
            Ordering on the vertices so that all edges go from left to right

        Raises:
           ValueError: If a cycle is found in the graph
        """
        ordering = []
        for key in self._vertices:
            vertex = self._vertices[key]
            vertex.state = self._UNDISCOVERED
        for key in self._vertices:
            vertex = self._vertices[key]
            if vertex.state == self._UNDISCOVERED:
                self._topologicalSort(self._startVertex, ordering)
        return ordering

    def _topologicalSort(self, vertex, ordering):
        """
        Recursive depth first search function implementing topological sort.
        Args:
           vertex: Vertex to search
           ordering: List of vertices in proper order
        """
        vertex.state = self._DISCOVERED
        for endpoint in vertex.endpoints:
            if endpoint.state == self._UNDISCOVERED:
                self._topologicalSort(endpoint, ordering)
            elif endpoint.state != self._EXPLORED:
                raise ValueError("Cycle found in graph (found '%s' while searching '%s')." % (vertex.name, endpoint.name))
        if vertex.name is not None:
            ordering.insert(0, vertex.name)
        vertex.state = self._EXPLORED


########################################################################
# PathResolverSingleton class definition
########################################################################


class PathResolverSingleton(object):

    """
    Singleton used for resolving executable paths.

    Various functions throughout Cedar Backup (including extensions) need a way
    to resolve the path of executables that they use.  For instance, the image
    functionality needs to find the ``mkisofs`` executable, and the Subversion
    extension needs to find the ``svnlook`` executable.  Cedar Backup's original
    behavior was to assume that the simple name (``"svnlook"`` or whatever) was
    available on the caller's ``$PATH``, and to fail otherwise.   However, this
    turns out to be less than ideal, since for instance the root user might not
    always have executables like ``svnlook`` in its path.

    One solution is to specify a path (either via an absolute path or some sort
    of path insertion or path appending mechanism) that would apply to the
    ``executeCommand()`` function.  This is not difficult to implement, but it
    seem like kind of a "big hammer" solution.  Besides that, it might also
    represent a security flaw (for instance, I prefer not to mess with root's
    ``$PATH`` on the application level if I don't have to).

    The alternative is to set up some sort of configuration for the path to
    certain executables, i.e. "find ``svnlook`` in ``/usr/local/bin/svnlook``" or
    whatever.  This PathResolverSingleton aims to provide a good solution to the
    mapping problem.  Callers of all sorts (extensions or not) can get an
    instance of the singleton.  Then, they call the ``lookup`` method to try and
    resolve the executable they are looking for.  Through the ``lookup`` method,
    the caller can also specify a default to use if a mapping is not found.
    This way, with no real effort on the part of the caller, behavior can neatly
    degrade to something equivalent to the current behavior if there is no
    special mapping or if the singleton was never initialized in the first
    place.

    Even better, extensions automagically get access to the same resolver
    functionality, and they don't even need to understand how the mapping
    happens.  All extension authors need to do is document what executables
    their code requires, and the standard resolver configuration section will
    meet their needs.

    The class should be initialized once through the constructor somewhere in
    the main routine.  Then, the main routine should call the :any:`fill` method to
    fill in the resolver's internal structures.  Everyone else who needs to
    resolve a path will get an instance of the class using :any:`getInstance` and
    will then just call the :any:`lookup` method.

    Attributes:
       _instance: Holds a reference to the singleton
       _mapping: Internal mapping from resource name to path
    """

    _instance = None  # Holds a reference to singleton instance

    class _Helper:
        """Helper class to provide a singleton factory method."""

        def __init__(self):
            pass

        def __call__(self, *args, **kw):
            # pylint: disable=W0212,R0201
            if PathResolverSingleton._instance is None:
                obj = PathResolverSingleton()
                PathResolverSingleton._instance = obj
            return PathResolverSingleton._instance

    getInstance = _Helper()  # Method that callers will use to get an instance

    def __init__(self):
        """Singleton constructor, which just creates the singleton instance."""
        PathResolverSingleton._instance = self
        self._mapping = {}

    def lookup(self, name, default=None):
        """
        Looks up name and returns the resolved path associated with the name.
        Args:
           name: Name of the path resource to resolve
           default: Default to return if resource cannot be resolved
        Returns:
            Resolved path associated with name, or default if name can't be resolved
        """
        value = default
        if name in list(self._mapping.keys()):
            value = self._mapping[name]
        logger.debug("Resolved command [%s] to [%s].", name, value)
        return value

    def fill(self, mapping):
        """
        Fills in the singleton's internal mapping from name to resource.
        Args:
           mapping (Dictionary mapping name to path, both as strings): Mapping from resource name to path

        """
        self._mapping = {}
        for key in list(mapping.keys()):
            self._mapping[key] = mapping[key]


########################################################################
# Pipe class definition
########################################################################


class Pipe(Popen):
    """
    Specialized pipe class for use by ``executeCommand``.

    The :any:`executeCommand` function needs a specialized way of interacting
    with a pipe.  First, ``executeCommand`` only reads from the pipe, and
    never writes to it.  Second, ``executeCommand`` needs a way to discard all
    output written to ``stderr``, as a means of simulating the shell
    ``2>/dev/null`` construct.
    """

    # noinspection PyArgumentList
    def __init__(self, cmd, bufsize=-1, ignoreStderr=False):
        stderr = STDOUT
        if ignoreStderr:
            devnull = nullDevice()
            stderr = os.open(devnull, os.O_RDWR)
        Popen.__init__(self, shell=False, args=cmd, bufsize=bufsize, stdin=None, stdout=PIPE, stderr=stderr)


########################################################################
# Diagnostics class definition
########################################################################


class Diagnostics(object):

    """
    Class holding runtime diagnostic information.

    Diagnostic information is information that is useful to get from users for
    debugging purposes.  I'm consolidating it all here into one object.

    """

    # pylint: disable=R0201

    def __init__(self):
        """
        Constructor for the ``Diagnostics`` class.
        """

    def __repr__(self):
        """
        Official string representation for class instance.
        """
        return "Diagnostics()"

    def __str__(self):
        """
        Informal string representation for class instance.
        """
        return self.__repr__()

    def getValues(self):
        """
        Get a map containing all of the diagnostic values.
        Returns:
            Map from diagnostic name to diagnostic value
        """
        values = {}
        values["version"] = self.version
        values["interpreter"] = self.interpreter
        values["platform"] = self.platform
        values["encoding"] = self.encoding
        values["locale"] = self.locale
        values["timestamp"] = self.timestamp
        return values

    def printDiagnostics(self, fd=sys.stdout, prefix=""):
        """
        Pretty-print diagnostic information to a file descriptor.
        Args:
           fd: File descriptor used to print information
           prefix: Prefix string (if any) to place onto printed lines
        *Note:* The ``fd`` is used rather than ``print`` to facilitate unit testing.
        """
        lines = self._buildDiagnosticLines(prefix)
        for line in lines:
            fd.write("%s\n" % line)

    def logDiagnostics(self, method, prefix=""):
        """
        Pretty-print diagnostic information using a logger method.
        Args:
           method: Logger method to use for logging (i.e. logger.info)
           prefix: Prefix string (if any) to place onto printed lines
        """
        lines = self._buildDiagnosticLines(prefix)
        for line in lines:
            method("%s" % line)

    def _buildDiagnosticLines(self, prefix=""):
        """
        Build a set of pretty-printed diagnostic lines.
        Args:
           prefix: Prefix string (if any) to place onto printed lines
        Returns:
            List of strings, not terminated by newlines
        """
        values = self.getValues()
        keys = list(values.keys())
        keys.sort()
        tmax = Diagnostics._getMaxLength(keys) + 3  # three extra dots in output
        lines = []
        for key in keys:
            title = key.title()
            title += (tmax - len(title)) * "."
            value = values[key]
            line = "%s%s: %s" % (prefix, title, value)
            lines.append(line)
        return lines

    @staticmethod
    def _getMaxLength(values):
        """
        Get the maximum length from among a list of strings.
        """
        tmax = 0
        for value in values:
            if len(value) > tmax:
                tmax = len(value)
        return tmax

    def _getVersion(self):
        """
        Property target to get the Cedar Backup version.
        """
        return "Cedar Backup %s (%s)" % (VERSION, DATE)

    def _getInterpreter(self):
        """
        Property target to get the Python interpreter version.
        """
        version = sys.version_info
        return "Python %d.%d.%d (%s)" % (version[0], version[1], version[2], version[3])

    def _getEncoding(self):
        """
        Property target to get the filesystem encoding.
        """
        return sys.getfilesystemencoding() or sys.getdefaultencoding()

    def _getPlatform(self):
        """
        Property target to get the operating system platform.
        """
        try:
            if sys.platform == "win32":
                sysname = "win32"
                release = platform.platform()
                machine = platform.machine()
                return "%s (%s %s)" % (sysname, release, machine)
            else:
                uname = os.uname()  # pylint: disable=no-member
                sysname = uname[0]  # i.e. Linux
                release = uname[2]  # i.e. 2.16.18-2
                machine = uname[4]  # i.e. i686
                return "%s (%s %s %s)" % (sys.platform, sysname, release, machine)
        except:
            return sys.platform

    def _getLocale(self):
        """
        Property target to get the default locale that is in effect.
        """
        try:
            import locale  # pylint: disable=import-outside-toplevel

            return locale.getdefaultlocale()[0]
        except:
            return "(unknown)"

    def _getTimestamp(self):
        """
        Property target to get a current date/time stamp.
        """
        try:
            import datetime  # pylint: disable=import-outside-toplevel

            return datetime.datetime.utcnow().ctime() + " UTC"
        except:
            return "(unknown)"

    version = property(_getVersion, None, None, "Cedar Backup version.")
    interpreter = property(_getInterpreter, None, None, "Python interpreter version.")
    platform = property(_getPlatform, None, None, "Platform identifying information.")
    encoding = property(_getEncoding, None, None, "Filesystem encoding that is in effect.")
    locale = property(_getLocale, None, None, "Locale that is in effect.")
    timestamp = property(_getTimestamp, None, None, "Current timestamp.")


########################################################################
# General utility functions
########################################################################

######################
# sortDict() function
######################


def sortDict(d):
    """
    Returns the keys of the dictionary sorted by value.
    Args:
       d: Dictionary to operate on
    Returns:
        List of dictionary keys sorted in order by dictionary value
    """
    items = list(d.items())
    items.sort(key=lambda x: (x[1], x[0]))  # sort by value and then by key
    return [key for key, value in items]


########################
# removeKeys() function
########################


def removeKeys(d, keys):
    """
    Removes all of the keys from the dictionary.
    The dictionary is altered in-place.
    Each key must exist in the dictionary.
    Args:
       d: Dictionary to operate on
       keys: List of keys to remove
    Raises:
       KeyError: If one of the keys does not exist
    """
    for key in keys:
        del d[key]


#########################
# convertSize() function
#########################


def convertSize(size, fromUnit, toUnit):
    """
    Converts a size in one unit to a size in another unit.

    This is just a convenience function so that the functionality can be
    implemented in just one place.  Internally, we convert values to bytes and
    then to the final unit.

    The available units are:

       - ``UNIT_BYTES`` - Bytes
       - ``UNIT_KBYTES`` - Kilobytes, where 1 kB = 1024 B
       - ``UNIT_MBYTES`` - Megabytes, where 1 MB = 1024 kB
       - ``UNIT_GBYTES`` - Gigabytes, where 1 GB = 1024 MB
       - ``UNIT_SECTORS`` - Sectors, where 1 sector = 2048 B

    Args:
       size (Integer or float value in units of ``fromUnit``): Size to convert
       fromUnit (One of the units listed above): Unit to convert from
       toUnit (One of the units listed above): Unit to convert to
    Returns:
        Number converted to new unit, as a float
    Raises:
       ValueError: If one of the units is invalid
    """
    if size is None:
        raise ValueError("Cannot convert size of None.")
    if fromUnit == UNIT_BYTES:
        byteSize = float(size)
    elif fromUnit == UNIT_KBYTES:
        byteSize = float(size) * BYTES_PER_KBYTE
    elif fromUnit == UNIT_MBYTES:
        byteSize = float(size) * BYTES_PER_MBYTE
    elif fromUnit == UNIT_GBYTES:
        byteSize = float(size) * BYTES_PER_GBYTE
    elif fromUnit == UNIT_SECTORS:
        byteSize = float(size) * BYTES_PER_SECTOR
    else:
        raise ValueError("Unknown 'from' unit %s." % fromUnit)
    if toUnit == UNIT_BYTES:
        return byteSize
    elif toUnit == UNIT_KBYTES:
        return byteSize / BYTES_PER_KBYTE
    elif toUnit == UNIT_MBYTES:
        return byteSize / BYTES_PER_MBYTE
    elif toUnit == UNIT_GBYTES:
        return byteSize / BYTES_PER_GBYTE
    elif toUnit == UNIT_SECTORS:
        return byteSize / BYTES_PER_SECTOR
    else:
        raise ValueError("Unknown 'to' unit %s." % toUnit)


##########################
# displayBytes() function
##########################


def displayBytes(bytes, digits=2):  # pylint: disable=W0622
    """
    Format a byte quantity so it can be sensibly displayed.

    It's rather difficult to look at a number like "72372224 bytes" and get any
    meaningful information out of it.  It would be more useful to see something
    like "69.02 MB".  That's what this function does.  Any time you want to display
    a byte value, i.e.::

       print "Size: %s bytes" % bytes

    Call this function instead::

       print "Size: %s" % displayBytes(bytes)

    What comes out will be sensibly formatted.  The indicated number of digits
    will be listed after the decimal point, rounded based on whatever rules are
    used by Python's standard ``%f`` string format specifier. (Values less than 1
    kB will be listed in bytes and will not have a decimal point, since the
    concept of a fractional byte is nonsensical.)

    Args:
       bytes (Integer number of bytes): Byte quantity
       digits (Integer value, typically 2-5): Number of digits to display after the decimal point
    Returns:
        String, formatted for sensible display
    """
    if bytes is None:
        raise ValueError("Cannot display byte value of None.")
    bytes = float(bytes)
    if math.fabs(bytes) < BYTES_PER_KBYTE:
        fmt = "%.0f bytes"
        value = bytes
    elif math.fabs(bytes) < BYTES_PER_MBYTE:
        fmt = "%." + "%d" % digits + "f kB"
        value = bytes / BYTES_PER_KBYTE
    elif math.fabs(bytes) < BYTES_PER_GBYTE:
        fmt = "%." + "%d" % digits + "f MB"
        value = bytes / BYTES_PER_MBYTE
    else:
        fmt = "%." + "%d" % digits + "f GB"
        value = bytes / BYTES_PER_GBYTE
    return fmt % value


##################################
# getFunctionReference() function
##################################


def getFunctionReference(module, function):
    """
    Gets a reference to a named function.

    This does some hokey-pokey to get back a reference to a dynamically named
    function.  For instance, say you wanted to get a reference to the
    ``os.path.isdir`` function.  You could use::

       myfunc = getFunctionReference("os.path", "isdir")

    Although we won't bomb out directly, behavior is pretty much undefined if
    you pass in ``None`` or ``""`` for either ``module`` or ``function``.

    The only validation we enforce is that whatever we get back must be
    callable.

    I derived this code based on the internals of the Python unittest
    implementation.  I don't claim to completely understand how it works.

    Args:
       module (Something like "os.path" or "CedarBackup3.util"): Name of module associated with function
       function (Something like "isdir" or "getUidGid"): Name of function
    Returns:
        Reference to function associated with name

    Raises:
       ImportError: If the function cannot be found
       ValueError: If the resulting reference is not callable

    @copyright: Some of this code, prior to customization, was originally part
    of the Python 2.3 codebase.  Python code is copyright (c) 2001, 2002 Python
    Software Foundation; All Rights Reserved.
    """
    parts = []
    if module is not None and module != "":
        parts = module.split(".")
    if function is not None and function != "":
        parts.append(function)
    copy = parts[:]
    while copy:
        try:
            module = __import__(".".join(copy))
            break
        except ImportError:
            del copy[-1]
            if not copy:
                raise
        parts = parts[1:]
    obj = module
    for part in parts:
        obj = getattr(obj, part)
    if not isinstance(obj, collections.abc.Callable):
        raise ValueError("Reference to %s.%s is not callable." % (module, function))
    return obj


#######################
# getUidGid() function
#######################


def getUidGid(user, group):
    """
    Get the uid/gid associated with a user/group pair

    This is a no-op if user/group functionality is not available on the platform.

    Args:
       user (User name as a string): User name
       group (Group name as a string): Group name
    Returns:
        Tuple ``(uid, gid)`` matching passed-in user and group
    Raises:
       ValueError: If the ownership user/group values are invalid
    """
    if _UID_GID_AVAILABLE:
        try:
            uid = pwd.getpwnam(user)[2]
            gid = grp.getgrnam(group)[2]
            return (uid, gid)
        except Exception as e:
            logger.debug("Error looking up uid and gid for [%s:%s]: %s", user, group, e)
            raise ValueError("Unable to lookup up uid and gid for passed in user/group.")
    else:
        return (0, 0)


#############################
# changeOwnership() function
#############################


def changeOwnership(path, user, group):
    """
    Changes ownership of path to match the user and group.

    This is a no-op if user/group functionality is not available on the
    platform, or if the either passed-in user or group is ``None``.  Further, we
    won't even try to do it unless running as root, since it's unlikely to work.

    Args:
       path: Path whose ownership to change
       user: User which owns file
       group: Group which owns file
    """
    if _UID_GID_AVAILABLE:
        if sys.platform == "win32":
            logger.debug("Chown not supported on Windows platform")
        elif user is None or group is None:
            logger.debug("User or group is None, so not attempting to change owner on [%s].", path)
        elif not isRunningAsRoot():
            logger.debug("Not root, so not attempting to change owner on [%s].", path)
        else:
            try:
                (uid, gid) = getUidGid(user, group)
                os.chown(path, uid, gid)  # pylint: disable=no-member
            except Exception as e:
                logger.error("Error changing ownership of [%s]: %s", path, e)


#############################
# isRunningAsRoot() function
#############################


def isRunningAsRoot():
    """
    Indicates whether the program is running as the root user.
    """
    if sys.platform == "win32":
        return False
    return os.getuid() == 0  # pylint: disable=no-member


##############################
# splitCommandLine() function
##############################


def splitCommandLine(commandLine):
    """
    Splits a command line string into a list of arguments.

    Unfortunately, there is no "standard" way to parse a command line string,
    and it's actually not an easy problem to solve portably (essentially, we
    have to emulate the shell argument-processing logic).  This code only
    respects double quotes (``"``) for grouping arguments, not single quotes
    (``'``).  Make sure you take this into account when building your command
    line.

    Incidentally, I found this particular parsing method while digging around in
    Google Groups, and I tweaked it for my own use.

    Args:
       commandLine (String, i.e. "cback3 --verbose stage store"): Command line string
    Returns:
        List of arguments, suitable for passing to ``popen2``

    Raises:
       ValueError: If the command line is None
    """
    if commandLine is None:
        raise ValueError("Cannot split command line of None.")
    fields = re.findall('[^ "]+|"[^"]+"', commandLine)
    fields = [field.replace('"', "") for field in fields]
    return fields


############################
# resolveCommand() function
############################


def resolveCommand(command):
    """
    Resolves the real path to a command through the path resolver mechanism.

    Both extensions and standard Cedar Backup functionality need a way to
    resolve the "real" location of various executables.  Normally, they assume
    that these executables are on the system path, but some callers need to
    specify an alternate location.

    Ideally, we want to handle this configuration in a central location.  The
    Cedar Backup path resolver mechanism (a singleton called
    :any:`PathResolverSingleton`) provides the central location to store the
    mappings.  This function wraps access to the singleton, and is what all
    functions (extensions or standard functionality) should call if they need to
    find a command.

    The passed-in command must actually be a list, in the standard form used by
    all existing Cedar Backup code (something like ``["svnlook", ]``).  The
    lookup will actually be done on the first element in the list, and the
    returned command will always be in list form as well.

    If the passed-in command can't be resolved or no mapping exists, then the
    command itself will be returned unchanged.  This way, we neatly fall back on
    default behavior if we have no sensible alternative.

    Args:
       command (List form of command, i.e. ``["svnlook", ]``): Command to resolve
    Returns:
        Path to command or just command itself if no mapping exists
    """
    singleton = PathResolverSingleton.getInstance()
    name = command[0]
    result = command[:]
    result[0] = singleton.lookup(name, name)
    return result


############################
# executeCommand() function
############################


def executeCommand(command, args, returnOutput=False, ignoreStderr=False, doNotLog=False, outputFile=None):
    """
    Executes a shell command, hopefully in a safe way.

    This function exists to replace direct calls to ``os.popen`` in the Cedar
    Backup code.  It's not safe to call a function such as ``os.popen()`` with
    untrusted arguments, since that can cause problems if the string contains
    non-safe variables or other constructs (imagine that the argument is
    ``$WHATEVER``, but ``$WHATEVER`` contains something like C{"; rm -fR ~/;
    echo"} in the current environment).

    Instead, it's safer to pass a list of arguments in the style supported bt
    ``popen2`` or ``popen4``.  This function actually uses a specialized ``Pipe``
    class implemented using either ``subprocess.Popen`` or ``popen2.Popen4``.

    Under the normal case, this function will return a tuple of C{(status,
    None)} where the status is the wait-encoded return status of the call per
    the ``popen2.Popen4`` documentation.  If ``returnOutput`` is passed in as
    ``True``, the function will return a tuple of ``(status, output)`` where
    ``output`` is a list of strings, one entry per line in the output from the
    command.  Output is always logged to the ``outputLogger.info()`` target,
    regardless of whether it's returned.

    By default, ``stdout`` and ``stderr`` will be intermingled in the output.
    However, if you pass in ``ignoreStderr=True``, then only ``stdout`` will be
    included in the output.

    The ``doNotLog`` parameter exists so that callers can force the function to
    not log command output to the debug log.  Normally, you would want to log.
    However, if you're using this function to write huge output files (i.e.
    database backups written to ``stdout``) then you might want to avoid putting
    all that information into the debug log.

    The ``outputFile`` parameter exists to make it easier for a caller to push
    output into a file, i.e. as a substitute for redirection to a file.  If this
    value is passed in, each time a line of output is generated, it will be
    written to the file using ``outputFile.write()``.  At the end, the file
    descriptor will be flushed using ``outputFile.flush()``.  The caller
    maintains responsibility for closing the file object appropriately.

    *Note:* I know that it's a bit confusing that the command and the arguments
    are both lists.  I could have just required the caller to pass in one big
    list.  However, I think it makes some sense to keep the command (the
    constant part of what we're executing, i.e. ``"scp -B"``) separate from its
    arguments, even if they both end up looking kind of similar.

    *Note:* You cannot redirect output via shell constructs (i.e. ``>file``,
    ``2>/dev/null``, etc.) using this function.  The redirection string would be
    passed to the command just like any other argument.  However, you can
    implement the equivalent to redirection using ``ignoreStderr`` and
    ``outputFile``, as discussed above.

    *Note:* The operating system environment is partially sanitized before
    the command is invoked.  See :any:`sanitizeEnvironment` for details.

    Args:
       command (List of individual arguments that make up the command): Shell command to execute
       args (List of additional arguments to the command): List of arguments to the command
       returnOutput (Boolean ``True`` or ``False``): Indicates whether to return the output of the command
       ignoreStderr (Boolean True or False): Whether stderr should be discarded
       doNotLog (Boolean ``True`` or ``False``): Indicates that output should not be logged
       outputFile (File as from ``open`` or ``file``, binary write): File that all output should be written to
    Returns:
        Tuple of ``(result, output)`` as described above
    """

    # I refactored this in Oct 2020 when modernizing the packaging. Recent versions of
    # Python gave a "ResourceWarning: unclosed file <_io.BufferedReader name=72>".  From
    # StackOverflow (https://stackoverflow.com/a/58696973/2907667), I decided that the solution
    # was to use the Pipe as a context manager, which helps ensure that all of its associated
    # resources are cleaned up properly.  However, the error handling below is somewhat
    # complicated, for reasons I am sure were important in 2004 but are not clear to me now.
    # The error conditions are also hard to test.  So, there's a chance that my refactoring is
    # not strictly equivalent to the original code.  If needed, the original code can be
    # found at this commit:
    #   https://github.com/pronovic/cedar-backup3/blob/370dbc9ea2b7a5ad9533605ead32d1e56746efd4/CedarBackup3/util.py#L1449

    logger.debug("Executing command %s with args %s.", command, args)
    outputLogger.info("Executing command %s with args %s.", command, args)
    if doNotLog:
        logger.debug("Note: output will not be logged, per the doNotLog flag.")
        outputLogger.info("Note: output will not be logged, per the doNotLog flag.")
    output = []
    fields = command[:]  # make sure to copy it so we don't destroy it
    fields.extend(args)
    try:
        sanitizeEnvironment()  # make sure we have a consistent environment
        with Pipe(fields, ignoreStderr=ignoreStderr) as pipe:
            try:
                while True:
                    line = pipe.stdout.readline()
                    if not line:
                        break
                    if returnOutput:
                        output.append(line.decode("utf-8"))
                    if outputFile is not None:
                        outputFile.write(line)
                    if not doNotLog:
                        outputLogger.info(line.decode("utf-8")[:-1])  # this way the log will (hopefully) get updated in realtime
                if outputFile is not None:
                    try:  # note, not every file-like object can be flushed
                        outputFile.flush()
                    except:
                        pass
                if returnOutput:
                    return (pipe.wait(), output)
                else:
                    return (pipe.wait(), None)
            except OSError as e:
                logger.debug("Command returned OSError: %s", e)
                if returnOutput:
                    if output != []:
                        return (pipe.wait(), output)
                    else:
                        return (pipe.wait(), [e])
                else:
                    return (pipe.wait(), None)
    except OSError as e:
        logger.debug("Command returned OSError: %s", e)
        if returnOutput:
            return (256, output)
        else:
            return (256, None)


##############################
# calculateFileAge() function
##############################


def calculateFileAge(path):
    """
    Calculates the age (in days) of a file.

    The "age" of a file is the amount of time since the file was last used, per
    the most recent of the file's ``st_atime`` and ``st_mtime`` values.

    Technically, we only intend this function to work with files, but it will
    probably work with anything on the filesystem.

    Args:
       path: Path to a file on disk

    Returns:
        Age of the file in days (possibly fractional)
    Raises:
       OSError: If the file doesn't exist
    """
    currentTime = int(time.time())
    fileStats = os.stat(path)
    lastUse = max(fileStats.st_atime, fileStats.st_mtime)  # "most recent" is "largest"
    ageInSeconds = currentTime - lastUse
    ageInDays = ageInSeconds / SECONDS_PER_DAY
    return ageInDays


###################
# mount() function
###################


def mount(devicePath, mountPoint, fsType):
    """
    Mounts the indicated device at the indicated mount point.

    For instance, to mount a CD, you might use device path ``/dev/cdrw``, mount
    point ``/media/cdrw`` and filesystem type ``iso9660``.  You can safely use any
    filesystem type that is supported by ``mount`` on your platform.  If the type
    is ``None``, we'll attempt to let ``mount`` auto-detect it.  This may or may
    not work on all systems.

    *Note:* This only works on platforms that have a concept of "mounting" a
    filesystem through a command-line ``"mount"`` command, like UNIXes.  It
    won't work on Windows.

    Args:
       devicePath: Path of device to be mounted
       mountPoint: Path that device should be mounted at
       fsType: Type of the filesystem assumed to be available via the device

    Raises:
       IOError: If the device cannot be mounted
    """
    if fsType is None:
        args = [devicePath, mountPoint]
    else:
        args = ["-t", fsType, devicePath, mountPoint]
    command = resolveCommand(MOUNT_COMMAND)
    result = executeCommand(command, args, returnOutput=False, ignoreStderr=True)[0]
    if result != 0:
        raise IOError("Error [%d] mounting [%s] at [%s] as [%s]." % (result, devicePath, mountPoint, fsType))


#####################
# unmount() function
#####################


def unmount(mountPoint, removeAfter=False, attempts=1, waitSeconds=0):
    """
    Unmounts whatever device is mounted at the indicated mount point.

    Sometimes, it might not be possible to unmount the mount point immediately,
    if there are still files open there.  Use the ``attempts`` and ``waitSeconds``
    arguments to indicate how many unmount attempts to make and how many seconds
    to wait between attempts.  If you pass in zero attempts, no attempts will be
    made (duh).

    If the indicated mount point is not really a mount point per
    ``os.path.ismount()``, then it will be ignored.  This seems to be a safer
    check then looking through ``/etc/mtab``, since ``ismount()`` is already in
    the Python standard library and is documented as working on all POSIX
    systems.

    If ``removeAfter`` is ``True``, then the mount point will be removed using
    ``os.rmdir()`` after the unmount action succeeds.  If for some reason the
    mount point is not a directory, then it will not be removed.

    *Note:* This only works on platforms that have a concept of "mounting" a
    filesystem through a command-line ``"mount"`` command, like UNIXes.  It
    won't work on Windows.

    Args:
       mountPoint: Mount point to be unmounted
       removeAfter: Remove the mount point after unmounting it
       attempts: Number of times to attempt the unmount
       waitSeconds: Number of seconds to wait between repeated attempts

    Raises:
       IOError: If the mount point is still mounted after attempts are exhausted
    """
    if os.path.ismount(mountPoint):
        for attempt in range(0, attempts):
            logger.debug("Making attempt %d to unmount [%s].", attempt, mountPoint)
            command = resolveCommand(UMOUNT_COMMAND)
            result = executeCommand(command, [mountPoint], returnOutput=False, ignoreStderr=True)[0]
            if result != 0:
                logger.error("Error [%d] unmounting [%s] on attempt %d.", result, mountPoint, attempt)
            elif os.path.ismount(mountPoint):
                logger.error("After attempt %d, [%s] is still mounted.", attempt, mountPoint)
            else:
                logger.debug("Successfully unmounted [%s] on attempt %d.", mountPoint, attempt)
                break  # this will cause us to skip the loop else: clause
            if attempt + 1 < attempts:  # i.e. this isn't the last attempt
                if waitSeconds > 0:
                    logger.info("Sleeping %d second(s) before next unmount attempt.", waitSeconds)
                    time.sleep(waitSeconds)
        else:
            if os.path.ismount(mountPoint):
                raise IOError("Unable to unmount [%s] after %d attempts." % (mountPoint, attempts))
            logger.info("Mount point [%s] seems to have finally gone away.", mountPoint)
        if os.path.isdir(mountPoint) and removeAfter:
            logger.debug("Removing mount point [%s].", mountPoint)
            os.rmdir(mountPoint)


###########################
# deviceMounted() function
###########################


def deviceMounted(devicePath):
    """
    Indicates whether a specific filesystem device is currently mounted.

    We determine whether the device is mounted by looking through the system's
    ``mtab`` file.  This file shows every currently-mounted filesystem, ordered
    by device.  We only do the check if the ``mtab`` file exists and is readable.
    Otherwise, we assume that the device is not mounted.

    *Note:* This only works on platforms that have a concept of an mtab file
    to show mounted volumes, like UNIXes.  It won't work on Windows.

    Args:
       devicePath: Path of device to be checked

    Returns:
        True if device is mounted, false otherwise
    """
    if os.path.exists(MTAB_FILE) and os.access(MTAB_FILE, os.R_OK):
        realPath = os.path.realpath(devicePath)
        with open(MTAB_FILE) as f:
            lines = f.readlines()
        for line in lines:
            (mountDevice, mountPoint, remainder) = line.split(None, 2)
            if mountDevice in [devicePath, realPath]:
                logger.debug("Device [%s] is mounted at [%s].", devicePath, mountPoint)
                return True
    return False


########################
# encodePath() function
########################


def encodePath(path):
    """
    Safely encodes a filesystem path as a Unicode string, converting bytes to fileystem encoding if necessary.
    Args:
       path: Path to encode
    Returns:
        Path, as a string, encoded appropriately
    Raises:
       ValueError: If the path cannot be encoded properly
    @see: http://lucumr.pocoo.org/2013/7/2/the-updated-guide-to-unicode/
    """
    if path is None:
        return path
    try:
        if isinstance(path, bytes):
            encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
            path = path.decode(encoding, "surrogateescape")  # to match what os.listdir() does
        return path
    except UnicodeError as e:
        raise ValueError("Path could not be safely encoded as %s: %s" % (encoding, str(e)))


######################
# pathJoin() function
######################


def pathJoin(path, *paths):
    """
    Wraps os.path.join(), normalizing slashes in the result.

    On Windows in particular, we often end up with mixed slashes, where parts of a path
    have forward slash and parts have backward slash.  This makes it difficult to construct
    exclusions in configuration, because you never know what part of a path will have
    what kind of slash.  I've decided to standardize on forward slashes.

    Returns:
        Result as from os.path.join() but always with forward slashes.
    """
    result = os.path.join(path, *paths)
    return result.replace("\\", "/")


########################
# nullDevice() function
########################


def nullDevice():
    """
    Attempts to portably return the null device on this system.

    The null device is something like ``/dev/null`` on a UNIX system.  The name
    varies on other platforms.
    """
    return os.devnull


##############################
# deriveDayOfWeek() function
##############################


def deriveDayOfWeek(dayName):
    """
    Converts English day name to numeric day of week as from ``time.localtime``.

    For instance, the day ``monday`` would be converted to the number ``0``.

    Args:
       dayName (string, i.e. ``"monday"``, ``"tuesday"``, etc): Day of week to convert
    Returns:
        Integer, where Monday is 0 and Sunday is 6; or -1 if no conversion is possible
    """
    if dayName.lower() == "monday":
        return 0
    elif dayName.lower() == "tuesday":
        return 1
    elif dayName.lower() == "wednesday":
        return 2
    elif dayName.lower() == "thursday":
        return 3
    elif dayName.lower() == "friday":
        return 4
    elif dayName.lower() == "saturday":
        return 5
    elif dayName.lower() == "sunday":
        return 6
    else:
        return -1  # What else can we do??  Thrown an exception, I guess.


###########################
# isStartOfWeek() function
###########################


def isStartOfWeek(startingDay):
    """
    Indicates whether "today" is the backup starting day per configuration.

    If the current day's English name matches the indicated starting day, then
    today is a starting day.

    Args:
       startingDay (string, i.e. ``"monday"``, ``"tuesday"``, etc): Configured starting day
    Returns:
        Boolean indicating whether today is the starting day
    """
    value = time.localtime().tm_wday == deriveDayOfWeek(startingDay)
    if value:
        logger.debug("Today is the start of the week.")
    else:
        logger.debug("Today is NOT the start of the week.")
    return value


#################################
# buildNormalizedPath() function
#################################


def buildNormalizedPath(path):
    """
    Returns a "normalized" path based on a path name.

    A normalized path is a representation of a path that is also a valid file
    name.  To make a valid file name out of a complete path, we have to convert
    or remove some characters that are significant to the filesystem -- in
    particular, the path separator, the Windows drive separator, and any
    leading ``'.'`` character (which would cause the file to be hidden in
    a file listing).

    Note that this is a one-way transformation -- you can't safely derive the
    original path from the normalized path.

    To normalize a path, we begin by looking at the first character.  If the
    first character is ``'/'`` or ``'\\'``, it gets removed.  If the first
    character is ``'.'``, it gets converted to ``'_'``.  Then, we look through the
    rest of the path and convert all remaining ``'/'`` or ``'\\'`` characters
    ``'-'``, and all remaining whitespace or ``':'`` characters to ``'_'``.

    As a special case, a path consisting only of a single ``'/'`` or ``'\\'``
    character will be converted to ``'_'``.  That's better than ``'-'``, because
    a dash tends to get interpreted by shell commands as a switch.

    As a special case, anything that looks like a leading Windows drive letter
    combination (like ``c:\\`` or ``c:/``) will be converted to something like
    ``c-``.  This is needed because a colon isn't a valid filename character
    on Windows.

    Args:
       path: Path to normalize

    Returns:
        Normalized path as described above

    Raises:
       ValueError: If the path is None
    """
    if path is None:
        raise ValueError("Cannot normalize path None.")
    elif len(path) == 0:
        return path
    elif path == "/" or path == "\\":
        return "_"
    else:
        normalized = path
        normalized = re.sub(r"(^[A-Za-z])(:)([\\/])", r"\1-", normalized)  # normalize Windows drive letter
        normalized = re.sub(r"^/", "", normalized)  # remove leading '/'
        normalized = re.sub(r"^\\", "", normalized)  # remove leading '\'
        normalized = re.sub(r"^\.", "_", normalized)  # convert leading '.' to '_' so file won't be hidden
        normalized = re.sub(r"/", "-", normalized)  # convert all '/' characters to '-'
        normalized = re.sub(r"\\", "-", normalized)  # convert all '\' characters to '-'
        normalized = re.sub(r"\s", "_", normalized)  # convert all whitespace to '_'
        normalized = re.sub(r":", "_", normalized)  # convert all remaining colons to '_'
        return normalized


#################################
# sanitizeEnvironment() function
#################################


def sanitizeEnvironment():
    """
    Sanitizes the operating system environment.

    The operating system environment is contained in ``os.environ``.  This method
    sanitizes the contents of that dictionary.

    Currently, all it does is reset the locale (removing ``$LC_*``) and set the
    default language (``$LANG``) to ``DEFAULT_LANGUAGE``.  This way, we can count
    on consistent localization regardless of what the end-user has configured.
    This is important for code that needs to parse program output.

    The ``os.environ`` dictionary is modifed in-place.  If ``$LANG`` is already
    set to the proper value, it is not re-set, so we can avoid the memory leaks
    that are documented to occur on BSD-based systems.

    Returns:
        Copy of the sanitized environment
    """
    for var in LOCALE_VARS:
        if var in os.environ:
            del os.environ[var]
    if LANG_VAR in os.environ:
        if os.environ[LANG_VAR] != DEFAULT_LANGUAGE:  # no need to reset if it exists (avoid leaks on BSD systems)
            os.environ[LANG_VAR] = DEFAULT_LANGUAGE
    return os.environ.copy()


#############################
# dereferenceLink() function
#############################


def dereferenceLink(path, absolute=True):
    """
    Deference a soft link, optionally normalizing it to an absolute path.
    Args:
       path: Path of link to dereference
       absolute: Whether to normalize the result to an absolute path
    Returns:
        Dereferenced path, or original path if original is not a link
    """
    if os.path.islink(path):
        result = os.readlink(path)
        if absolute and not os.path.isabs(result):
            result = os.path.abspath(os.path.join(os.path.dirname(path), result))
        return result
    return path


#########################
# checkUnique() function
#########################


def checkUnique(prefix, values):
    """
    Checks that all values are unique.

    The values list is checked for duplicate values.  If there are
    duplicates, an exception is thrown.  All duplicate values are listed in
    the exception.

    Args:
       prefix: Prefix to use in the thrown exception
       values: List of values to check

    Raises:
       ValueError: If there are duplicates in the list
    """
    values.sort()
    duplicates = []
    for i in range(1, len(values)):
        if values[i - 1] == values[i]:
            duplicates.append(values[i])
    if duplicates:
        raise ValueError("%s %s" % (prefix, duplicates))


#######################################
# parseCommaSeparatedString() function
#######################################


def parseCommaSeparatedString(commaString):
    """
    Parses a list of values out of a comma-separated string.

    The items in the list are split by comma, and then have whitespace
    stripped.  As a special case, if ``commaString`` is ``None``, then ``None``
    will be returned.

    Args:
       commaString: List of values in comma-separated string format
    Returns:
        Values from commaString split into a list, or ``None``
    """
    if commaString is None:
        return None
    else:
        pass1 = commaString.split(",")
        pass2 = []
        for item in pass1:
            item = item.strip()
            if len(item) > 0:
                pass2.append(item)
        return pass2
