# website.py

""" Website is a module that contains functions for extracting tables from websites. """

from boxfish.data import config
from boxfish.data import soups

from boxfish.utils.dicts import extract_values, get_subset
from boxfish.utils import drivers, lists, urls


# Main functions
def extract(url, config):
    """ Get data from a website based on config and url

    data = extract(url=url, config=config):

    Args:
        url (str or list):  url
        config (dict):      configuration

    Returns:
        data (list): List of rows (list) of columns (str)
    """

    [poutput] = extract_values(config, ['output'])
    data = extract_data(url,config)
    save(data, poutput)

    return data


def extract_data(url,config):
    """ Extract data from url to list

    data = extract_data(url, config)

    Args:
        url (str or list):  url
        config (dict):      configuration

    Returns:
        data (list): List of rows (list) of columns (str)
    """

    data = []

    if url and config:
        adriver = drivers.driver_start(config['driver'])
        try:
            data = _extract_data_from_driver(url, config, adriver)
        finally:
            drivers.driver_stop(adriver)

    return data


# Beautiful Soup functions
def extract_table(page, ptable, url=''):
    """ Extract table from an HTML page

        atable = extract_table(page, ptable, url)

        Args:
            page(str): HTML text
            ptable(dict): Table parameters with keys config.TABLEKEYS
            url(str): Url current page
        Returns:
            atable (list): List of rows (list) of columns (str)
    """

    atable = []

    if page:
        soup = soups.get_soup(page)

        if soup:
            # Pre-processing
            for s in soup.select('style'):
                s.decompose()
            if url:
                soup = soups.set_urls(soup, url)
            soups.wrap_navigable_strings(soup)

            pparams = get_subset(ptable, config.TABLEKEYS)
            atable = soups.extract_table(soup, **pparams)
    return atable


def extract_url_next_page(page, pnext_page, url):
    """ Extract url that refers to next page

        url_next = extract_url_next_page(page,pnext_page,url)

        Args:
            page(str): HTML text
            next_page(dict): Next page parameters with keys config.PAGEKEYS
            url(str): Url current page

        Returns:
            url_next_page (str): Url next page
    """
    url_next_page = ''
    tf = not soups.is_empty_filter(pnext_page['rows']) if pnext_page else False

    if tf:
        [index] = extract_values(pnext_page, ['index'])
        index = index if index else -1

        pnext_page['include_strings'] = False
        pnext_page['include_links'] = True

        alinks = extract_table(page, pnext_page, url)
        if alinks:
            alinks = lists.flatten(alinks)
            url_next_page = alinks[index]
    return  url_next_page


# File functions
def save(data, fileconfig):
    """ Save data to CSV file

        save(data, fileconfig)

        Args:
            data(dataframe or list): Data from HTML
            fileconfig(dict): Parameter with keys {'filename','date_format','replace'}

        Returns:
            None
    """
    lists.to_csv(data, fileconfig['filename'],
             date_format=fileconfig['date_format'],
             overwrite=fileconfig['overwrite'],
             quoting=fileconfig['quoting'])

# Private functions
def _extract_data_from_driver(url, config, adriver):
    """ Extract data from url to list

    data = _extract_data_from_driver(url, config, adriver)

    Args:
        url (str or list):  url
        config (dict):      configuration
        adriver (driver):   driver

    Returns:
        data (list): List of rows (list) of columns (str)
    """
    data = []

    # Extract parameters
    [phtml] = extract_values(config, ['html'])
    [ptable] = extract_values(phtml, ['table'])
    [ppage] = extract_values(phtml, ['page'])

    i_request = 0
    url = lists.to_list(url) if not isinstance(url, list) else url

    for url_i in url:
        url_next = url_i
        url_pre = ['']
        while url_next not in url_pre:
            page = drivers.request_page(adriver, url=url_next, count=i_request)
            i_request = i_request + 1

            table = extract_table(page, ptable, url_next)
            data.extend(table)

            url_pre.append(url_next)
            url_next = extract_url_next_page(page, ppage, url_next)
    return data