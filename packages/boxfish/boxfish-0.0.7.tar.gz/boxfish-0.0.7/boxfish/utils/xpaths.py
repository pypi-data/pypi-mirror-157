# xpaths.py

"""Xpaths is a module that contains functions for working with xpaths
"""

from boxfish.utils.lists import to_list
from boxfish.utils.strings import to_int


# Xpath list functions
def is_child(axpath, axpaths):
    """ Returns true is axpath is a child from an item in axpaths

        tf = is_child(axpath, axpaths)

        Args:
            axpath(str): xpath
            axpaths(str or list): xpath list

        Returns:
            tf (bool): true if axpath is a child of item in axpaths
        """
    axpaths = to_list(axpaths) if not isinstance(axpaths, list) else axpaths
    tf = False
    i = 0
    while not tf and i < len(axpaths):
        tf = _is_child(axpath, axpaths[i])
        i = i + 1
    return tf


def is_descendant(axpath, axpaths):
    """ Returns true is axpath is a descdendant from an item in axpaths

        tf = is_child(axpath, axpaths)

        Args:
            axpath(str): xpath
            axpaths(str or list): xpath list

        Returns:
            tf (bool): true if axpath is a descendant of item in axpaths
        """
    axpaths = to_list(axpaths) if not isinstance(axpaths, list) else axpaths
    tf = False
    i = 0
    while not tf and i < len(axpaths):
        tf = _is_descendant(axpath, axpaths[i])
        i = i + 1
    return tf


def parent(axpath):
    """ Returns xpath of parent of axpath

        pxpath = parent(axpath)

        Args:
            axpath(str): xpath

        Returns:
            pxpath(str): xpath parent
        """
    sep  = '/'
    stripped = axpath.split(sep,-1)
    return sep.join(stripped[:-1])


def split(axpath):
    """ Returns two lists with xpath name attributes and indices

    [anames aindices] = split(xpath)

    Args:
        axpath(str): Xpath

    Returns:
        anames (list): list with names
        aindices (list): list with indices
    """
    anames = axpath.split('/')
    aindices = [1] * len(anames)
    for i in range(len(anames)-1, -1, -1):
        if anames[i] == '':
            anames.pop(i)
            aindices.pop(i)
        else:
            tlist = anames[i].replace('[', ']').split(sep=']')
            anames[i] = tlist[0]
            if len(tlist) > 1:
                index = to_int(tlist[1])
                aindices[i] = index if index else 1
    return anames, aindices


# Private functions

def _is_child(axpath, bxpath):
    """ Returns true if axpath is a child of bxpath

     tf = _is_child(axpath, bxpath)

     Args:
         axpath(str): xpath
         bxpath(str): xpath

     Returns:
         tf (bool): true if axpath is a child of bxpath
     """

    [anames, aidx] = split(axpath)
    [bnames, bidx] = split(bxpath)
    tf = len(anames) == len(bnames) + 1
    if tf:
        tf = tf and anames[:-1] == bnames
        tf = tf and aidx[:-1] == bidx
    return tf


def _is_descendant(axpath, bxpath):
    """ Returns true if axpath is a descendant of bxpath

     tf = _is_descendant(axpath, bxpath)

     Args:
         axpath(str): xpath
         bxpath(str): xpath

     Returns:
         tf (bool): true if axpath is a desdendant of bxpath
     """

    [anames, aidx] = split(axpath)
    [bnames, bidx] = split(bxpath)
    levels = len(anames) - len(bnames)
    tf = levels >= 1
    if tf:
        tf = tf and anames[:-levels] == bnames
        tf = tf and aidx[:-levels] == bidx
    return tf
