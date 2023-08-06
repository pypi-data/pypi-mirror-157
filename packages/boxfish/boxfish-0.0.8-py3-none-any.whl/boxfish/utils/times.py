# times.py

"""Times is a module that contains functions that interact with times and dates"""

import time

DATE_JAPANESE = '%Y-%m-%d'
DATETIME_JAPANESE = '%Y-%m-%d %H:%M:%S'
DATETIME_FILE = '%Y%m%d%H%M%S'
DATE_FILE = '%Y%m%d'
TIME_FILE = '%H%M%S'


# Strings
def strftime(t=None, string='', sep=' ', date_format=DATETIME_JAPANESE, string_first=False):
    """ Return a formatted string which contains date/time and a text string

    str = strftime(t=None, string='', sep=' ', date_format=DATETIME_JAPANESE, string_first=True)

    Args:
        t (float or tuple or time.struct_time): date/time
        string (str): Input string
        sep (str): Seperator between date and time and string
        date_format (str): Date and time format
        string_first (bool): Returns string first if True else t first

    Returns:
        str (str): Output string which contains input string and date/time

    Example:
        >>> strftime(t=time.time(),string='Hello World', sep=' ')
        '2021-05-01 18:08:31 Hello World'
    """
    strdatetime = time.strftime(date_format) if t is None else time.strftime(date_format, to_struct_time(t))
    return string + sep + strdatetime if string_first else strdatetime + sep + string


def strfdate(t=None, string='', sep=' ', date_format=DATE_JAPANESE, string_first=False):
    """ Return a formatted string which contains date and a text string

    str = strfdate(t=None, string='', sep=' ', date_format=DATE_JAPANESE, string_first=False):

    Args:
        t (float or tuple or time.struct_time): date
        string (str): Input string
        sep (str): Seperator between date  and string
        date_format (str): Date format
        string_first (bool): Returns string first if True else t first

    Returns:
        str (str): Output string which contains input string and date

    Example:
        >>> strfdate(t=time.time(),string='Hello World', sep=' ')
        '2021-05-01 Hello World'
    """

    return strftime(t=t, string=string, sep=sep, date_format=date_format, string_first=string_first)


# Conversion
def to_float(t=None):
    """Convert time t to type float. Returns current time if no time is provided

        t = to_float()

    Args:
        t (struct_time or tuple): Time as struct_time or tuple

    Returns:
        t (float): Time as float

    Raises:
          OverflowError or ValueError for invalid time t
    """

    t = time.time() if t is None else t

    if not isinstance(t, tuple) and not isinstance(t, time.struct_time) \
            and not isinstance(t, int) and not isinstance(t, float):
        raise ValueError

    ftime = time.mktime(t) if isinstance(t, tuple) or isinstance(t, time.struct_time) else t

    return ftime


def to_struct_time(t=None):
    """Convert time t to type time.struct_time. Returns current time if no time is provided

        t = to_struct_time()

    Args:
        t (float or tuple): Time as float or float

    Returns:
        t (tuple): Time as a struct_time

    Raises:
          OverflowError or ValueError for invalid time t
    """

    t = time.time() if t is None else t
    stime = time.localtime(t) if isinstance(t, float) else time.struct_time(t)

    return stime


def to_tuple(t=None):
    """Convert time t to type tuple. Returns current time if no time is provided

        t = to_tuple()

    Args:
        t (float or struct_time): Time as float or struct_time

    Returns:
        t (tuple): Time as a tuple

    Raises:
          OverflowError or ValueError for invalid time t
    """

    t = time.time() if t is None else t
    stime = time.localtime(t) if isinstance(t, float) else t

    return (stime.tm_year, stime.tm_mon, stime.tm_mday, stime.tm_hour, stime.tm_min,
            stime.tm_sec, stime.tm_wday, stime.tm_yday, stime.tm_isdst)


# Sleep
def sleep_on_count(adict, cnt):
    """ Sleeps dict[counter] seconds if cnt+1 is a multiple of counter

    Or: when iterating over cnt, sleep_on_count pauses for dict[counter] seconds every counter iterations

    sleep_on_count(adict, cnt)

    Args:
        adict (dict) Keys are counters (int), values are seconds (int)
        cnt (int) Current counter

    Returns:
        None
    """

    for counter, sec in adict.items():
        if (cnt + 1) % int(counter) == 0:
            time.sleep(sec)


def sleep_until(end_time):
    """ Sleeps until end_time

    sleep_until(end_time)

    Args:
        end_time (struct_time or float or tuple)

    Returns:
        None
    """

    end_time = to_float(end_time)
    time.sleep(max(end_time - time.time(), 0))
