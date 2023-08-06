# strings.py

"""Strings is a module that contains general functions for working with strings"""

import os
import time

DATE_FILE = '%Y%m%d'


# General
def rstrip_endswith(string, endswith):
    """ Strip the right-most characters endswith from string

    str = rstrip_endswith(string, endswith):

    Args:
        string (str): input string
        endswith (str): string to be stripped from the right of string

    Returns:
        str (str): stripped string
    """
    return string[:-len(endswith)] if string.endswith(endswith) else string


def replace_newlines(string, replace_string=''):
    """ Replace any new line characters (\\r, \\n, \\r\\n) with replace_string

    str = replace_newlines(string, replace_string='')

    Args:
        string (str): input string
        replace_string (str): string that replaces newline characters

    Returns:
        str (str): stripped string
    """
    return replace_string.join(string.splitlines())


def is_int(string):
    """ Returns true if string represents an integer

    tf = is_int(string)

    Args:
        string (str): input string

    Returns:
        tf (bool): True if string represents int, False otherwise
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_float(string):
    """ Returns true if string represents a float

    tf = is_float(string)

    Args:
        string (str): input string

    Returns:
        tf (bool): True if string represents float, False otherwise
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def to_int(string):
    """ Converts a string to int

    aint = to_int(string)

    Args:
        string (str): input string

    Returns:
        aint (int or None): int representation of astring
    """
    return int(float(string)) if is_float(string) else None


def to_float(string):
    """ Converts a string to float

    afloat = to_float(string)

    Args:
        string (str): input string

    Returns:
        afloat (int or None): float representation of astring
    """
    return float(string) if is_float(string) else None


def get_type(obj):
    """ Return type as string

    astr = get_type(obj)

    Args:
        obj : object

    Returns:
        astr (str): string of type
    """
    astr = str(type(obj))
    alist = astr.split("'")
    if len(alist)>1:
        astr = alist[1]
    else:
        astr = ''
    return astr


# Regex

def re_literals(string):
    """ Regex conversion of string creating literals for regex meta characters

        restring = re_literals(string)

        Args:
            string (str): input string

        Returns:
            restring (str): Regex string
        """
    re_chars = ['\\', '^', '$', '.', '|', '?', '*', '+', '(', ')', '[', ']', '{', '}']
    restring = string

    for char in re_chars:
        restring = restring.replace(char, '\\' + char)

    return restring


# Filenames
def filename_append_date(filename, date_format=DATE_FILE):
    """ Filename with current date appended

    filename_date = filename_append_date(filename, date_format)

    Args:
        filename (str): Filename
        date_format (str): Date in strftime format
    Returns:
        filename_date (str): Filename with current date appended

    Example:
        filename = r'D:\filename.ext'
        date_format = '%Y%m%d'
        filename_date = filename_append_date(filename, date_format)
        >> 'filename20210513.ext'
    """
    file_pre, file_extension = os.path.splitext(filename)
    return file_pre + time.strftime(date_format) + file_extension


def filename_append_extension(filename, default_extension):
    """ Filename with default extension appended

    filename_ext = filename_append_extension(filename, default_extension)

    Args:
        filename (str): Filename
        default_extension (str): Default extension

    Returns:
        filename_ext (str): Filename with default extension appended

    Raises:
          TypeError in case default_extension is not a valid extension

    Example:
        filename = 'filename'
        default_extension = '.py'
        filename_ext = filename_append_extension(filename, default_extension)
        >> 'filename.py'

        filename = r'D:\filename'
        default_extension = '.py'
        filename_ext = filename_append_extension(filename, default_extension)
        >> 'D:\\filename.py'
    """
    filename, file_extension = os.path.splitext(filename)
    file_extension = default_extension if not file_extension else ''
    if not file_extension[0] == '.':
        raise TypeError

    return filename + file_extension
