# dicts.py

"""Dicts is a module that contains functions for dictionaries"""

import json


def get_subset(adict, akeys):
    """ Get a dict subset consisting of akeys. Missing akeys are ignored

    bdict = get_subset(adict, akeys)

    Args:
        adict (dict): Dictionary with key-value pairs
        akeys (list): List of key strings
    Returns:
        bdict (dict): Dictionary with key-value pairs based on akeys in adict


    Example:
        adict = {'key1': val1, 'key2': val1}
        bdict = get_subset(adict, ['key1', 'key3'])
        >> bdict = {'key1': val1}
    """
    return {key: value for key, value in adict.items() if key in akeys}


def extract_values(adict, akeys):
    """ Extract values from adict for akeys

    [values1, values2, ...] = extract_values(adict, alist)

    Args:
        adict (dict): Dictionary with key-value pairs
        akeys (list): List of key strings
    Returns:
        values (list): List of values from adict. The number of output values
                       is identical to the length of alist. Missing keys result in None values

    Example:
        adict = {'key1': val1, }
        [val1, val3] = extract_values(adict, ['key1', 'key3'])
        >> val1 = 'val1'
        >> val3 = None
    """

    klist = [None]*len(akeys)
    for i, val in enumerate(akeys):
        if val in adict:
            klist[i] = adict[val]
    return [*klist]


def append(adict, bdict):
    """ Append bdict to adict

    Duplicate entries in bdict overwrite entries from adict

    [values1, values2, ...] = extract_values(adict, alist)

    Args:
        adict (dict): Dictionary with key-value pairs
        bdict (dict): Dictionary to be appended
    Returns:
        cdict (dict): Result dictionary

    Example:
        adict = {'key1': 'val1', 'key2': 'val2'}
        bdict = {'key1': 'bval1', 'key3': 'val3'}
        cdict = append(adict, bdict)
        >> {'key1': 'bval1', 'key2': 'val2', 'key3': 'val3'}
    """
    return dict(adict, **bdict) if isinstance(bdict, dict) else adict


def remove_nones(adict):
    """ Remove key-vlaue pairs with a None Value

    [values1, values2, ...] = extract_values(adict, alist)

    Args:
        adict (dict): Dictionary with key-value pairs
    Returns:
        bdict (dict): Result dictionary

    Example:
        adict = {'key1': 'val1', 'key2': None,'key3': 'val3'}
        bdict = remove_nones(adict)
        >> {'key1': 'bval1', 'key3': 'val3'}
    """
    return {k: v for k, v in adict.items() if v is not None}


def dumps(adict):
    """ Dumps dictionary into Json string. Generalizes to lists

        ajson = dumps(adict)

        Args:
            adict (dict or list): Dictionary
        Returns:
            ajson (str or list): Json strings
        """
    ajson = ''
    if isinstance(adict, dict):
        ajson = json.dumps(adict)
    elif isinstance(adict, list):
        ajson = [json.dumps(idict) for idict in adict]
    return ajson


def loads(ajson):
    """ Loads Json string into a dictionary. Generalizes to lists

        adict = loads(ajson)

        Args:
            ajson (str or list): Json strings
        Returns:
            adict (dict or list): Dictionary
        """
    adict = {}
    if isinstance(ajson, str):
        adict = json.loads(ajson)
    elif isinstance(ajson, list):
        adict = [json.loads(ijson) for ijson in ajson]
    return adict


def set_(alist):
    """ Return a set of unique dictionaries in alist

        aset = set_(alist)

        Args:
            alist (list): List of dictionary
        Returns:
            aset (list): List of dictionary
        """
    aset = []
    if isinstance(alist, list):
        ajson = dumps(alist)
        ujson = list(set(ajson))
        aset = loads(ujson)
    return aset
