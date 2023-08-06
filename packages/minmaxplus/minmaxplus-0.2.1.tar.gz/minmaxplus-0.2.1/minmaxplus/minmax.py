#! /usr/bin/python3
# -*- coding: utf-8 -*-

#############################################################################
# MinMax+  extends builtin min and max functions.
# Copyright (C) 2021 alexpdev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
############################################################################
"""
# MinMax+

A small library of functions that extend python's builtin `min` and `max` function.


"""

import sys


class InputError(Exception):
    """Input Type is not an iterable sequence."""

    def __init__(self, value):
        """
        Initialize Exception for Input Error

        Parameters
        ----------
        value : `Any`
            Uninterpretable input value.
        """
        message = f"Input type cannot be indexed.  {value}"
        super().__init__(message)

class EmptySequenceError(Exception):
    """Input iterable is empty."""

    def __init__(self, value):
        """
        Initialize Exception for Sequence Error.

        Parameters
        ----------
        value : `Any`
            Empty sequence value.
        """
        message = f"Input iterable is empty.  {value}"
        super().__init__(message)

def maxp(seq):
    """
    Return the maximum element and it's index within the sequence.

    Parameters
    ----------
    seq : `iterable`
        An iterable sequence that implements the `__getitem__` or `index` method.

    Returns
    -------
    `tuple` :
        the maximum element, and it's index
    """
    if len(seq) == 0:
        return None, None
    if not hasattr(seq, "index"):
        raise InputError

    maxn, maxi, n = -sys.maxsize, 0, len(seq)
    if isinstance(seq[0], str):
        maxn = chr(0)

    if n & 1: n -= 1  # checks if seq length is odd
    for i in range(0, n, 2):
        if seq[i + 1] > seq[i]:
            maximum, index = seq[i + 1], i + 1
        else:
            maximum, index = seq[i], i
        if maximum > maxn:
            maxn, maxi = maximum, index

    # checks if seq length is odd
    if len(seq) & 1:
        if seq[n] > maxn:
            maxn, maxi = seq[n], n
    return (maxn, maxi)


def minp(seq):
    """
    Return the minimum element and it's index within the sequence.

    Parameters
    ----------
    seq : `iterable`
        An iterable sequence that implements the `__getitem__` or `index` method.

    Returns
    -------
    `tuple` :
        the minimum element, and it's index
    """
    if not hasattr(seq, "index"):
        raise InputError
    if len(seq) == 0:
        raise EmptySequenceError

    minn, mini, n = sys.maxsize, 0, len(seq)
    if isinstance(seq[0], str):
        minn = chr(1114111)

    if n & 1: n -= 1   # checks if seq length is odd
    for i in range(0, n, 2):
        if seq[i + 1] < seq[i]:
            minimum, index = seq[i + 1], i + 1
        else:
            minimum, index = seq[i], i
        if minimum < minn:
            minn, mini = minimum, index

    # checks if seq length is odd
    if len(seq) & 1:
        if seq[n] < minn:
            minn, mini = seq[n], n
    return (minn, mini)


def minmaxp(seq):
    """
    Return the minimum and maximum element and their indexed locations.

    Parameters
    ----------
    seq : `iterable`
        An iterable sequence that implements the `__getitem__` or `index` method.

    Returns
    -------
    `tuple` :
        The minimum element, maximum element and their indexed locations.
    """
    if not hasattr(seq, "index"):
        raise InputError
    if len(seq) == 0:
        raise EmptySequenceError

    maxn, maxi, n = -sys.maxsize, 0, len(seq)
    minn, mini = sys.maxsize, 0
    if isinstance(seq[0], str):
        maxn = chr(0)
        minn = chr(1114111)

    if n & 1: n -= 1   # checks if seq length is odd
    for i in range(0, n, 2):
        if seq[i + 1] > seq[i]:
            maximum, maxindex = seq[i + 1], i + 1
            minimum, minindex = seq[i], i
        else:
            minimum, minindex = seq[i + 1], i + 1
            maximum, maxindex = seq[i], i
        if maximum > maxn:
            maxn, maxi = maximum, maxindex
        if minimum < minn:
            minn, mini = minimum, minindex

    # checks if seq length is odd
    if len(seq) & 1:
        if seq[n] > maxn:
            maxn, maxi = seq[n], n
        if seq[n] < minn:
            minn, mini = seq[n], n
    return [(minn, mini), (maxn, maxi)]
