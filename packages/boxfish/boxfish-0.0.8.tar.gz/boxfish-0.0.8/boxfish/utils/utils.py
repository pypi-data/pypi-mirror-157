# utils.py

"""Utils is a module that contains utility functions without need of their own module"""

import json
import os
import shutil
from pathlib import Path


# Files
def makedir(spath):
    """ Make a new directory

        Args:
            spath (str): Full path of new directory
        Returns:
            None

        Example:
    """
    try:
        Path(spath).mkdir(parents=True, exist_ok=True)
    except OSError:
        print('Parent folder does not exist')


def create_folder_if_not_exist(folder):
    """ Create folder

        Args:
            folder (str): Full path of new folder
        Returns:
            None

        Example:
    """
    if folder and not os.path.exists(folder):
        os.makedirs(folder)


def read(filename, filetype='text', encoding='utf-8'):
    """ Read text from file

        text = read(filename)

        Args:
            filename (str): file name
            filetype (str): file type ('text' or 'json')
            encoding (str): file encoding

        Returns:
            text (str or json):
    """

    text = {} if filetype == 'json' else ''

    try:
        with open(filename, "r", encoding=encoding) as file:
            if filetype == 'json':
                text = json.load(file)
            else:
                text = file.read()

    except IOError:
        print('Error: File does not appear to exist.')
    return text


def read_json(filename, encoding='utf-8'):
    """ Read json from file

        ajson = read(filename)

        Args:
            filename (str): file name
            encoding (str): file encoding

        Returns:
            ajson (dict)
    """
    return read(filename, filetype='json', encoding=encoding)


def write(filename, text, filetype='text', encoding='utf-8', indent=4):
    """ Write text to file

        write(filename)

        Args:
            filename (str): file name of configuration
            text (str or dict): text
            filetype (str): file type ('text' or 'json')
            encoding (str): file encoding
            indent (int): text indentation

        Returns:
            None

        Raises:
            IOError (): error in case function cannot write to filename
    """

    try:
        with open(filename, "w", encoding=encoding) as file:
            if filetype == 'json':
                json.dump(text, file, indent=indent)
            else:
                file.write(text)
    except IOError:
        print('Error: Cannot write to file.')


def write_json(filename, ajson, encoding='utf-8', indent=4):
    """ Write json to file

        write_json(filename, text, indent=4)

        Args:
            filename (str): file name of configuration
            ajson (dict): dictionary
            encoding (str): file encoding
            indent (int): text indentation

        Returns:
            None

        Raises:
            IOError (): error in case function cannot write to filename
    """
    write(filename, ajson, filetype='json', encoding=encoding, indent=indent)


def flip(filename1, filename2):
    """ Flips to files.

        flip(filename1, filename2)

        Args:
            filename1 (str): file name of configuration
            filename2 (str): file name of configuration

        Returns:
            None

        Raises:
            IOError (): error in case function cannot write to filename
    """
    filename0 = filename1 + '.tmp'
    if os.path.isfile(filename1) and os.path.isfile(filename2):
        shutil.copy(filename1, filename0)
        shutil.copy(filename2, filename1)
        shutil.move(filename0, filename2)

