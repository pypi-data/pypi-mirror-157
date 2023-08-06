# lists.py

"""Lists is a module that contains functions for lists"""

import csv
import os
from boxfish.utils.strings import filename_append_date
from boxfish.utils.utils import create_folder_if_not_exist


# General
def is_empty(alist):
    """ Returns true if list is empty or contains '' or None only

    tf = is_empty(alist)

    Args:
        alist (list): List
    Returns:
        tf (bool): True if list is empty or contains '' or None only

    Example:
        alist = [None, None]
        tf = is_empty(alist)
        >> True

        alist = ['', '']
        tf = is_empty(alist)
        >> True

        alist = [0, '']
        tf = is_empty(alist)
        >> False
    """
    return all(item == '' or item is None for item in alist)


def flatten(alist):
    """ Merges a list of lists of items into a single list of items

    Source: https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists

    flist = flatten(alist)

    Args:
        alist (list): List of lists of items
    Returns:
        flist (bool): List of items

    Example:
        alist = [1,2,3]
        blist = [1, alist, 2*alist]
        blist
        >> [1, [1, 2, 3], [1, 2, 3, 1, 2, 3]]

        flist = flatten()
        flist
        >> [1, 1, 2, 3, 1, 2, 3, 1, 2, 3]
    """
    def f(x): return [x] if not isinstance(x, list) else x
    return [item for sublist in alist for item in f(sublist)]


def unique(alist):
    """ Return list with duplicates removed

    ulist = unique(alist)

    Args:
        alist (list): List of items
    Returns:
        ulist (list): List of unique items from alist


    Example:
        alist = (1,2,3,3,4,5)
        ulist = unique(alist)
        >> ulist = (1,2,3,4,5)
    """
    return list(set(alist))


def is_equal_length(*args):
    """ Returns true if all inputs are lists and have the same length

    tf = is_equal_lenght(alist,blist)

    Args:
        *args:
            alist (list): List of items
    Returns:
        tf: True if all inputs are lists and have the same length


    Example:
        alist = [1,2,3,4,5]
        blist = [2,4,6,7,10]
        >> tf = is_equal_length(alist,blist)
    """
    tf = True
    length = None
    for arg in args:
        tf = tf and isinstance(arg, list)
        tf = tf and (length == len(arg) or length is None)
        length = len(arg) if length is None else length
    return tf


def to_list(*args):
    """ Returns a list with the items in args

    alist = to_list(*args)

    Args:
        *args: list of items
    Returns:
        alist (list): list of items in *args


    Example:
        a = 1
        b = 'Hello'
        >> alist = to_list(a, b)
    """
    return [value for value in args]


def reshape(*args):
    """ Reshape returns a tuple of lists of the same length in case
    all list arguments have the same length L.
    All non-list arguments are converted to a list of length L by duplication.
    Otherwise, the function returns a tuple of None

    alist = reshape(*args)

    Args:
        *args: arguments
    Returns:
        alists: List of lists of same length as args

    Example:
        a = [1, 2, 3, 4]
        b = 5
        c = None
        d = 'Hello'
        >> [a2,b2,c2,d2] = reshape(a, b, c, d)
    """
    arglists = [arg if isinstance(arg, list) else to_list(arg) for arg in args]
    lenlists = [len(i) for i in arglists]
    length = max(lenlists)
    is_valid = all(alen == length or alen == 1 for alen in lenlists)
    return (length*alist if len(alist) == 1 else alist for alist in arglists) if is_valid \
        else tuple([None for _ in arglists])

# I/O functions


def to_csv(alist, filename, date_format='', overwrite=False, header=None, quoting=csv.QUOTE_NONNUMERIC):
    """ Save list to csv file

    fullname = to_csv(alist, filename, date_format, overwrite)

    Args:
        alist (list): list of rows (lists)
        filename (str): Filename
        # Optional
        date_format (str): Date format in strftime format. Date is added to filename
        overwrite (bool): Overwrite existing file if True else append
        header (list): Header
        quoting (int): CSV quoting constant
    Returns:
        fullname: Full filename including date

    Example:
        fullname = to_csv(alist, 'file.csv', date_format='%Y%m%d, overwrite=True)
    """
    if (alist is not None) and os.path.basename(filename):
        create_folder_if_not_exist(os.path.dirname(filename))
        fullname = filename_append_date(filename, date_format)

        if os.path.exists(fullname) and not overwrite:
            with open(fullname, 'a', newline='', encoding='utf-8') as f:
                csv_writer = csv.writer(f, quoting=quoting)
                if not is_empty(header):
                    csv_writer.writerow(header)
                csv_writer.writerows(alist)
        else:
            with open(fullname, 'wt', newline='', encoding='utf-8') as f:
                csv_writer = csv.writer(f, quoting=quoting)
                if header:
                    csv_writer.writerow(header)
                csv_writer.writerows(alist)
    else:
        fullname = ''
    return fullname


def from_csv(filename, quoting=csv.QUOTE_NONNUMERIC):
    """ Load list from csv file

        alist = from_csv(filename)

        Args:
            filename (str): Filename
            quoting (int): CSV quoting constant
        Returns:
            alist (list): list of rows (lists)

        Example:
            alist = from_csv('file.csv')
        """
    alist = []
    if os.path.exists(filename):
        with open(filename, 'r', newline='') as f:
            csv_reader = csv.reader(f, quoting=quoting)
            for row in csv_reader:
                alist.append(row)
    return alist


# Set functions. Set functions remove duplicates
def intersect(alist, blist):
    """ Return list with intersection of alist and blist

    clist = intersect(alist, blist)

    Args:
        alist (list): List of items
        blist (list): List of items
    Returns:
        clist (list): List of intersection of items from alist and blist


    Example:
        alist = [1,2,3,4,5]
        blist = [2,4,6]
        clist = intesect(alist, blist)
        >> clist = (2,4)
    """
    return list(set(alist) & set(blist))


def union(alist, blist):
    """ Return list with union of alist and blist

    clist = union(alist, blist)

    Args:
        alist (list): List of items
        blist (list): List of items
    Returns:
        clist (list): List of union of items from alist and blist


    Example:
        alist = [1,2,3,3,4,5]
        blist = [2,4,6]
        clist = union(alist, blist)
        >> clist = (1,2,3,4,5,6)
    """
    return list(set(alist) | set(blist))


def difference(alist, blist):
    """ Return list with difference of alist and blist

    clist = difference(alist, blist)

    Args:
        alist (list): List of items
        blist (list): List of items
    Returns:
        clist (list): List of difference of items from alist and blist


    Example:
        alist = [1,2,3,3,4,5]
        blist = [2,4,6]
        clist = difference(alist, blist)
        >> clist = (1,3,5)
    """
    return list(set(alist) - set(blist))


def is_subset(alist, blist):
    """ Return true if alist is a subset of blist

    tf = is_susbet(alist, blist)

    Args:
        alist (list): List of items
        blist (list): List of items
    Returns:
        tf (bool): True if all items of alist are in blist, False otherwise


    Example:
        alist = [1,2,3]
        blist = [6,5,4,3,2,1]
        tf = is_subset(alist, blist)
        >> tf = True
    """
    return set(alist).issubset(set(blist))


def is_disjoint(alist, blist):
    """ Return true if alist and blist are disjoint

    tf = is_disjoint(alist, blist)

    Args:
        alist (list): List of items
        blist (list): List of items
    Returns:
        tf (bool): True if no items of alist and blist are identical


    Example:
        alist = [1,2,3]
        blist = [4,5,6]
        tf = is_disjoint(alist, blist)
        >> tf = True
    """
    return is_empty(intersect(alist, blist))
