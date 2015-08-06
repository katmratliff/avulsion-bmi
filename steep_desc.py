#! /usr/local/bin/python
import numpy as np


def lowest_neighbor(n, sub):
    """Find lowest neighbor value around a point.

    Parameters
    ----------
    n : ndarray
        Grid of elevations.
    sub : tuple of int
        Row/column subscript into elevation matrix.

    Returns
    -------
    tuple of int
        Subscripts into elevation matrix of the lowest neighbor.
    """
    i, j = sub

    if j == n.shape[1] - 1:
        di, dj  = np.array([0, 1, 1]), np.array([-1, -1, 0])
    elif j == 0:
        di, dj  = np.array([1, 1, 0]), np.array([0, 1, 1])
    else:
        di, dj = np.array([0, 1, 1, 1, 0]),  np.array([-1, -1, 0, 1, 1])

    lowest = np.argmin(n[i + di, j + dj])
    return i + di[lowest], j + dj[lowest]


def below_sea_level(z, sea_level):
    """Check if an elevation is below sea level.

    Parameters
    ----------
    z : float
        Elevation.
    sea_level : float
        Elevation of sea level.

    Returns
    -------
    boolean
        `True` if at or below sea level. Otherwise, `False`.
    """
    return z <= sea_level


def at_river_mouth(z, sub, z0):
    """Check if a cell is at the river mouth.

    Parameters
    ----------
    z : ndarray
        2D-array of elevations.
    sub : tuple of int
        Row and column subscript into *z*.
    z0 : float
        Elevation of sea level (or `None`).

    Returns
    -------
    boolean
        True if the cell at the given subscript is at the river mouth.
    """
    try:
        return sub[0] == z.shape[0] - 1 or below_sea_level(z[sub], z0)
    except IndexError:
        return True


def find_course(z, i, j, riv_len, sea_level=None):
    """Find the course of a river.

    Given a river course as subscripts, (*i*, *j*), into an array of
    elevations, (*z*), find the river path until the coast (*sea_level*) or
    the end of the domain.

    Parameters
    ----------
    z : ndarray
        Grid elevations.
    i : array_like of int
        Row subscripts (into *n*) for river.
    j : array_like of int
        Column subscripts (into *n*) for river.
    riv_len : int
        Current length of the river in cells.
    sea_level : None, optional
        The current sea level.

    Examples
    --------
    >>> import numpy as np

    >>> z = np.array([[4., 3., 4.], [2., 3., 3.], [2., 1., 2.]])
    >>> riv_i, riv_j = np.zeros(9, dtype=int), np.zeros(9, dtype=int)
    >>> riv_i[0], riv_j[0] = 0, 1

    >>> new_len = find_course(z, riv_i, riv_j, 1)
    >>> new_len
    3
    >>> riv_i[:new_len], riv_j[:new_len]
    (array([0, 1, 2]), array([1, 0, 1]))

    >>> new_len = find_course(z, riv_i, riv_j, 1, sea_level=2.)
    >>> new_len
    2
    >>> riv_i[:new_len], riv_j[:new_len]
    (array([0, 1]), array([1, 0]))
    """
    # function to find the steepest descent route
    # note: this needs to be improved to remove potential bias that may occur
    # if two or more cells have the steepest descent elevation
    if sea_level is None:
        sea_level = - np.finfo(float).max

    for n in xrange(riv_len, i.size):
        if at_river_mouth(z, (i[n - 1], j[n - 1]), sea_level):
            break

        i[n], j[n] = lowest_neighbor(z, (i[n - 1], j[n - 1]))

    try:
        return n
    except NameError:
        raise RuntimeError('river length larger than ij-buffer')
