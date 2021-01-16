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
# Copyright (c) 2004-2005,2010,2015 Kenneth J. Pronovici.
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
# Purpose  : Provides knapsack algorithms used for "fit" decisions
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########
# Notes
########

"""
Provides the implementation for various knapsack algorithms.

Knapsack algorithms are "fit" algorithms, used to take a set of "things" and
decide on the optimal way to fit them into some container.  The focus of this
code is to fit files onto a disc, although the interface (in terms of item,
item size and capacity size, with no units) is generic enough that it can
be applied to items other than files.

All of the algorithms implemented below assume that "optimal" means "use up as
much of the disc's capacity as possible", but each produces slightly different
results.  For instance, the best fit and first fit algorithms tend to include
fewer files than the worst fit and alternate fit algorithms, even if they use
the disc space more efficiently.

Usually, for a given set of circumstances, it will be obvious to a human which
algorithm is the right one to use, based on trade-offs between number of files
included and ideal space utilization.  It's a little more difficult to do this
programmatically.  For Cedar Backup's purposes (i.e. trying to fit a small
number of collect-directory tarfiles onto a disc), worst-fit is probably the
best choice if the goal is to include as many of the collect directories as
possible.

:author: Kenneth J. Pronovici <pronovic@ieee.org>
"""

#######################################################################
# Public functions
#######################################################################

######################
# firstFit() function
######################


def firstFit(items, capacity):

    """
    Implements the first-fit knapsack algorithm.

    The first-fit algorithm proceeds through an unsorted list of items until
    running out of items or meeting capacity exactly.  If capacity is exceeded,
    the item that caused capacity to be exceeded is thrown away and the next one
    is tried.  This algorithm generally performs more poorly than the other
    algorithms both in terms of capacity utilization and item utilization, but
    can be as much as an order of magnitude faster on large lists of items
    because it doesn't require any sorting.

    The "size" values in the items and capacity arguments must be comparable,
    but they are unitless from the perspective of this function.  Zero-sized
    items and capacity are considered degenerate cases.  If capacity is zero,
    no items fit, period, even if the items list contains zero-sized items.

    The dictionary is indexed by its key, and then includes its key.  This
    seems kind of strange on first glance.  It works this way to facilitate
    easy sorting of the list on key if needed.

    The function assumes that the list of items may be used destructively, if
    needed.  This avoids the overhead of having the function make a copy of the
    list, if this is not required.  Callers should pass ``items.copy()`` if they
    do not want their version of the list modified.

    The function returns a list of chosen items and the unitless amount of
    capacity used by the items.

    Args:
       items (dictionary, keyed on item, of ``item, size`` tuples, item as string and size as integer): Items to operate on
       capacity (integer): Capacity of container to fit to
    Returns:
        Tuple ``(items, used)`` as described above
    """

    # Use dict since insert into dict is faster than list append
    included = {}

    # Search the list as it stands (arbitrary order)
    used = 0
    remaining = capacity
    for key in list(items.keys()):
        if remaining == 0:
            break
        if remaining - items[key][1] >= 0:
            included[key] = None
            used += items[key][1]
            remaining -= items[key][1]

    # Return results
    return (list(included.keys()), used)


#####################
# bestFit() function
#####################


def bestFit(items, capacity):

    """
    Implements the best-fit knapsack algorithm.

    The best-fit algorithm proceeds through a sorted list of items (sorted from
    largest to smallest) until running out of items or meeting capacity exactly.
    If capacity is exceeded, the item that caused capacity to be exceeded is
    thrown away and the next one is tried.  The algorithm effectively includes
    the minimum number of items possible in its search for optimal capacity
    utilization.  For large lists of mixed-size items, it's not ususual to see
    the algorithm achieve 100% capacity utilization by including fewer than 1%
    of the items.  Probably because it often has to look at fewer of the items
    before completing, it tends to be a little faster than the worst-fit or
    alternate-fit algorithms.

    The "size" values in the items and capacity arguments must be comparable,
    but they are unitless from the perspective of this function.  Zero-sized
    items and capacity are considered degenerate cases.  If capacity is zero,
    no items fit, period, even if the items list contains zero-sized items.

    The dictionary is indexed by its key, and then includes its key.  This
    seems kind of strange on first glance.  It works this way to facilitate
    easy sorting of the list on key if needed.

    The function assumes that the list of items may be used destructively, if
    needed.  This avoids the overhead of having the function make a copy of the
    list, if this is not required.  Callers should pass ``items.copy()`` if they
    do not want their version of the list modified.

    The function returns a list of chosen items and the unitless amount of
    capacity used by the items.

    Args:
       items (dictionary, keyed on item, of ``item, size`` tuples, item as string and size as integer): Items to operate on
       capacity (integer): Capacity of container to fit to
    Returns:
        Tuple ``(items, used)`` as described above
    """

    # Use dict since insert into dict is faster than list append
    included = {}

    # Sort the list from largest to smallest
    itemlist = list(items.items())
    itemlist.sort(key=lambda x: x[1][1], reverse=True)  # sort descending
    keys = []
    for item in itemlist:
        keys.append(item[0])

    # Search the list
    used = 0
    remaining = capacity
    for key in keys:
        if remaining == 0:
            break
        if remaining - items[key][1] >= 0:
            included[key] = None
            used += items[key][1]
            remaining -= items[key][1]

    # Return the results
    return (list(included.keys()), used)


######################
# worstFit() function
######################


def worstFit(items, capacity):

    """
    Implements the worst-fit knapsack algorithm.

    The worst-fit algorithm proceeds through an a sorted list of items (sorted
    from smallest to largest) until running out of items or meeting capacity
    exactly.  If capacity is exceeded, the item that caused capacity to be
    exceeded is thrown away and the next one is tried.  The algorithm
    effectively includes the maximum number of items possible in its search for
    optimal capacity utilization.  It tends to be somewhat slower than either
    the best-fit or alternate-fit algorithm, probably because on average it has
    to look at more items before completing.

    The "size" values in the items and capacity arguments must be comparable,
    but they are unitless from the perspective of this function.  Zero-sized
    items and capacity are considered degenerate cases.  If capacity is zero,
    no items fit, period, even if the items list contains zero-sized items.

    The dictionary is indexed by its key, and then includes its key.  This
    seems kind of strange on first glance.  It works this way to facilitate
    easy sorting of the list on key if needed.

    The function assumes that the list of items may be used destructively, if
    needed.  This avoids the overhead of having the function make a copy of the
    list, if this is not required.  Callers should pass ``items.copy()`` if they
    do not want their version of the list modified.

    The function returns a list of chosen items and the unitless amount of
    capacity used by the items.

    Args:
       items (dictionary, keyed on item, of ``item, size`` tuples, item as string and size as integer): Items to operate on
       capacity (integer): Capacity of container to fit to
    Returns:
        Tuple ``(items, used)`` as described above
    """

    # Use dict since insert into dict is faster than list append
    included = {}

    # Sort the list from smallest to largest
    itemlist = list(items.items())
    itemlist.sort(key=lambda x: x[1][1])  # sort ascending
    keys = []
    for item in itemlist:
        keys.append(item[0])

    # Search the list
    used = 0
    remaining = capacity
    for key in keys:
        if remaining == 0:
            break
        if remaining - items[key][1] >= 0:
            included[key] = None
            used += items[key][1]
            remaining -= items[key][1]

    # Return results
    return (list(included.keys()), used)


##########################
# alternateFit() function
##########################


def alternateFit(items, capacity):

    """
    Implements the alternate-fit knapsack algorithm.

    This algorithm (which I'm calling "alternate-fit" as in "alternate from one
    to the other") tries to balance small and large items to achieve better
    end-of-disk performance.  Instead of just working one direction through a
    list, it alternately works from the start and end of a sorted list (sorted
    from smallest to largest), throwing away any item which causes capacity to
    be exceeded.  The algorithm tends to be slower than the best-fit and
    first-fit algorithms, and slightly faster than the worst-fit algorithm,
    probably because of the number of items it considers on average before
    completing.  It often achieves slightly better capacity utilization than the
    worst-fit algorithm, while including slighly fewer items.

    The "size" values in the items and capacity arguments must be comparable,
    but they are unitless from the perspective of this function.  Zero-sized
    items and capacity are considered degenerate cases.  If capacity is zero,
    no items fit, period, even if the items list contains zero-sized items.

    The dictionary is indexed by its key, and then includes its key.  This
    seems kind of strange on first glance.  It works this way to facilitate
    easy sorting of the list on key if needed.

    The function assumes that the list of items may be used destructively, if
    needed.  This avoids the overhead of having the function make a copy of the
    list, if this is not required.  Callers should pass ``items.copy()`` if they
    do not want their version of the list modified.

    The function returns a list of chosen items and the unitless amount of
    capacity used by the items.

    Args:
       items (dictionary, keyed on item, of ``item, size`` tuples, item as string and size as integer): Items to operate on
       capacity (integer): Capacity of container to fit to
    Returns:
        Tuple ``(items, used)`` as described above
    """

    # Use dict since insert into dict is faster than list append
    included = {}

    # Sort the list from smallest to largest
    itemlist = list(items.items())
    itemlist.sort(key=lambda x: x[1][1])  # sort ascending
    keys = []
    for item in itemlist:
        keys.append(item[0])

    # Search the list
    used = 0
    remaining = capacity

    front = keys[0 : len(keys) // 2]
    back = keys[len(keys) // 2 : len(keys)]
    back.reverse()

    i = 0
    j = 0

    while remaining > 0 and (i < len(front) or j < len(back)):
        if i < len(front):
            if remaining - items[front[i]][1] >= 0:
                included[front[i]] = None
                used += items[front[i]][1]
                remaining -= items[front[i]][1]
            i += 1
        if j < len(back):
            if remaining - items[back[j]][1] >= 0:
                included[back[j]] = None
                used += items[back[j]][1]
                remaining -= items[back[j]][1]
            j += 1

    # Return results
    return (list(included.keys()), used)
