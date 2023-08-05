# drivers.py

"""Drivers is a module that contains functions to access HTML pages via HTTP."""

import os
import requests
from selenium import webdriver
from boxfish.utils import dicts, times, urls, utils

DRIVERKEYS = ['package', 'sleep', 'requests', 'selenium']
REQUESTSKEYS = ['headers', 'timeout']
SELENIUMKEYS = ['filename', 'log', 'headless']
MIN_TIMEOUT = 10


def get_page(url='', params=None, count=0):
    """ Get single HTTP page from an url with the default driver

    page = get_page(url):

    Args:
        url (str): url
        params (dict): driver parameters
        count (int): page request counter

    Returns:
        page (str): HTML text
    """

    params = create_params() if params is None else params
    adriver = driver_start(params)
    try:
        page = request_page(adriver, url=url, params=params, count=count)
    finally:
        driver_stop(adriver)
    return page


def request_page(driver, url='', params=None, count=0):
    """ Request a single HTTP page from an url with driver

    page = request_page(driver, url):

    Args:
        driver (object): A driver object.Supported drivers are:
                         requests.sessions.Session or selenium.webdriver
        url (str): url
        params (dict): driver parameters
        count (int): page request counter

    Returns:
        page (str): HTML text

    Errors:
        HTTPError
        ConnectionError
        Timeout
        RequestException
    """

    params = create_params() if params is None else params
    [psleep] = dicts.extract_values(params, ['sleep'])
    page = ''
    try:
        if urls.is_valid_http(url):
            is_requests = isinstance(driver, requests.sessions.Session)
            is_selenium = isinstance(driver, webdriver.firefox.webdriver.WebDriver) or \
                          isinstance(driver, webdriver.chrome.webdriver.WebDriver)
            if is_requests:
                headers = driver.headers if 'headers' in dir(driver) else ''
                timeout = max(driver.timeout if 'timeout' in dir(driver) else MIN_TIMEOUT, MIN_TIMEOUT)
                r = driver.get(url, headers=headers, timeout=timeout)
                r.encoding = 'utf-8'
                page = r.text
            elif is_selenium:
                driver.get(url)
                page = driver.page_source
            else:
                page = ''
            times.sleep_on_count(psleep, count)
        else:
            page = utils.read(url) if os.path.isfile(url) else ''

    except requests.exceptions.HTTPError as e:
        print("Http Error:", e)
    except requests.exceptions.ConnectionError as e:
        print("Error Connecting:", e)
    except requests.exceptions.Timeout as e:
        print("Timeout Error:", e)
    except requests.exceptions.RequestException as e:
        print("RequestException: ", e)

    return page


def create_params(package='requests', headers=None, timeout=1, filename='', log='', sleep=None, headless=True):
    """ Create driver parameters

    params = create_params(package='requests', headers='', timeout=1, filename='', log='', headless=True):

    Args:
        package (str): Name of the driver package. Supported packages are 'selenium' and 'requests'
        headers (dict): Driver headers
        timeout (int): Timeout between driver calls, in seconds
        filename (str): File name for data output
        log (str): File name for log file
        sleep (dict): Sleep dictionary
        headless (bool): Start driver in headless mode if true

    Returns:
        params (dict): Driver parameters
    """

    headers = {} if headers is None else headers

    params = dict.fromkeys(DRIVERKEYS, {})
    params['package'] = package if package in ('selenium', 'requests') else 'requests'
    params['sleep'] = sleep if isinstance(sleep, dict) else {}

    params['requests'] = dict.fromkeys(REQUESTSKEYS, {})
    params['requests']['headers'] = headers
    params['requests']['timeout'] = max(timeout, MIN_TIMEOUT)

    params['selenium'] = dict.fromkeys(SELENIUMKEYS, {})
    params['selenium']['filename'] = filename
    params['selenium']['log'] = log
    params['selenium']['headless'] = headless
    return params


def driver_start(params=None):
    """ Start driver

    driver = driver_start(params)

    Args:
        params (dict): Driver parameters with keys DRIVERKEYS

    Returns:
        driver (obj): Driver object. Supported objects are:
                      requests.sessions.Session or selenium.webdriver
    """

    driver = None

    if isinstance(params, dict):
        if params['package'] == 'requests':
            driver = requests.Session()
            driver.headers = params['requests']['headers']
            driver.timeout = params['requests']['timeout']
        elif params['package'] == 'selenium':
            if 'gecko' in params['selenium']['filename']:
                options = webdriver.firefox.options.Options()
                options.headless = params['selenium']['headless']
                driver = webdriver.Firefox(executable_path=params['selenium']['filename'],
                                           service_log_path=params['selenium']['log'],
                                           options=options)
            elif 'chrome' in params['selenium']['filename']:
                options = webdriver.chrome.options.Options()
                options.headless = params['selenium']['headless']
                str_log = "--log-path=" + params['selenium']['log']
                driver = webdriver.Chrome(executable_path=params['selenium']['filename'],
                                          service_args=["--verbose", str_log],
                                          options=options)
            else:
                # TODO error handling
                print('Driver not found')
    return driver


def driver_stop(driver):
    """ Stop driver

    driver_stop(driver)

    Args:
        driver (obj): Driver object. Supported objects are:
                      requests.sessions.Session or selenium.webdriver

    Returns:
        None
    """

    if driver:
        is_selenium = isinstance(driver, webdriver.firefox.webdriver.WebDriver) or \
                      isinstance(driver, webdriver.chrome.webdriver.WebDriver)
        if is_selenium:
            driver.close()
