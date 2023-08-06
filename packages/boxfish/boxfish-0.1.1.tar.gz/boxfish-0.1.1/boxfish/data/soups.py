# soups.py

"""Soups is a module that contains functions for the Beautiful Soup library.

Objects
soup (bs4.BeautifulSoup): A BS4 object of an HTML page
tag  (bs4.element.Tag): A BS4 object of part of an HTML page
ResultSet (): A BS4 object of parts of an HTML page

aitem : soup or tag or ResultSet object
aitems: ResultSet object
atable (list): List of rows (list) of columns (str)

afilter (dict): BS4 filter on keys 'elem' (str) and 'class' (list)
FILTERKEYS = ['elem', 'class']

"""

import copy
import collections

import bs4
from bs4 import BeautifulSoup

from boxfish.utils import dicts, lists, urls, utils
from boxfish.utils.xpaths import split as xsplit


# Main functions
def get_page(aitem):
    """ Get page from soup, tag or ResultSet object

    page = get_page(bitem)

    Args:
        aitem : soup or tag or ResultSet object

    Returns:

        page (str): HTML page
    """

    page = None
    if aitem is not None:
        if is_tag(aitem) or is_soup(aitem):
            page = aitem.decode()
        elif is_results(aitem):
            alist = [atag.decode() for atag in aitem]
            page = "\n".join(alist)
    return page


def get_soup(page):
    """ Get soup object from page

    soup = get_soup(page)

    Args:
        page (str): HTML page or an open file handle

    Returns:
        soup (bs4.BeautifulSoup): A BS4 object of an HTML page
    """

    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
    else:
        soup = None
    return soup


def extract_table(soup, id=None, rows=None, cols=None, include_strings=True, include_links=False):
    """ Extract table from soup

    [atable] = extract_table(soup, id = {}, rows = rows, cols = cols)

    Args:
        soup (bs4.BeautifulSoup): A BS4 object of an HTML page
        id (dict): dict with keys {'elem','class'}
        rows (dict): dict with keys {'elem','class'}
        cols (list): list of dict with keys {'elem','class'}
        include_strings (boolean): Include strings if true
        include_links (boolean): Include links if true

    Returns:
        atable (list): List of rows (list) of columns (str)
    """

    atable = []
    id = {} if id is None else id

    if all(val is not None for val in [soup, rows]):
        # Extract rows
        # TODO Change ID
        new_soup = find_item(soup, id) if id else None
        soup = new_soup if new_soup else soup
        results = find_items(soup, rows)

        # Extract columns of all rows
        atable = to_table(results, cols, include_strings=include_strings, include_links=include_links)
    return atable


def to_table(aitem, cols=None, include_strings=True, include_links=False):
    """ Convert aitem to a table

    [atable] = to_table(aitem, cols=None, include_strings=True, include_links=False)

    Args:
        aitem(tag or ResultSet): BS4 object
        # Extract subset of strings
        cols (list): list of dict with keys {'elem','class'}
        # Extract all strings
        include_strings (boolean): Include strings if true
        include_links (boolean): Include links if true
    Returns:
        atable (list): List of rows (list) of columns (str)
    """
    atable = []
    if not is_results(aitem):
        aitem = [aitem]

    for record in aitem:
        row = get_text(record, cols=cols, include_strings=include_strings, include_links=include_links)
        if not lists.is_empty(row):
            atable.append(row)

    return atable


# Editing functions - deep copy
def set_base(page, url):
    """ Set <base> in page with url

    [bpage] = set_base(page, url)

    Args:
        page (str): HTML page
        url (str): URL link

    Returns:
        bpage (str): HTML page with <base>

    """
    asoup = get_soup(page)

    # Set base
    abase = asoup.find('base')
    if not abase:
        abase = asoup.new_tag('base')
    abase["href"] = url

    # Add base to head
    ahead = asoup.find('head')
    if not ahead:
        ahead = asoup.new_tag('head')
        asoup.append(ahead)
    ahead.append(abase)

    bpage = get_page(asoup)
    return bpage


def split(soup):
    """ Split HTML soup into objects meta and body. Meta and body are deep copies.

    [meta, body] = split(soup)

    Args:
        soup (bs4.BeautifulSoup): A BS4 object of an HTML page with <html> tag

    Returns:
        meta (bs4.BeautifulSoup): Contains HTML outside <body> plus empty body
        body (bs4.element.Tag): Contains HTML inside <body>

    """
    meta = None
    body = None

    if soup is not None and soup.html is not None:
        meta = copy.copy(soup)
        body = meta.find("body")
        if body is None:
            body = BeautifulSoup('<body>', 'html.parser').find("body")
        else:
            body.extract()
        meta.html.append(BeautifulSoup('<body>', 'html.parser').find("body"))
    return meta, body


def merge(meta, body):
    """ Merge HTML meta and body into a soup object. Soup contains deep copies of meta and body

    [soup] = merge(meta, body)

    Args:
        meta (bs4.BeautifulSoup): Contains HTML outside <body> plus empty body
        body (tag or ResultSet): Contains HTML inside <body>

    Returns:
        soup (bs4.BeautifulSoup): A BS4 object of an HTML page with <html> tag

    """
    if meta is not None and body is not None:
        # Create body with <body>
        body = to_body(body)

        # Meta
        soup = copy.copy(meta)
        # Extract current body
        body_curr = soup.find("body")
        if body_curr is not None:
            body_curr.extract()

        # Insert new body
        body_new = copy.copy(body)
        soup.html.append(body_new)
    else:
        soup = None
    return soup


def set_urls(aitem, url):
    """ Set full url paths to all href tags. Returns a deep copy

    [titem] = set_urls(aitem, url)

    Args:
        aitem(tag or soup): BS4 object
        url (str): url string

    Returns:
        aitem(tag or soup): BS4 object with full url strings

    """
    if is_tag(aitem) or is_soup(aitem):
        titem = copy.copy(aitem)
        if url:
            results = titem.find_all('a')
            results.append(titem)
            for aitem in results:
                if 'href' in aitem.attrs:
                    if not urls.is_valid_http(aitem['href']):
                        aitem['href'] = urls.update_relative_path(url, aitem['href'])
    else:
        titem = None
    return titem


# Conversion functions
def to_body(aitem):
    """ Convert aitem to tag with <body>

    body = to_body(aitem)

    Args:
        aitem(tag or ResultSet): BS4 object

    Returns:
        body (tag): tag with a <body>
    """
    if is_tag(aitem):
        if aitem.name == 'body':
            body = aitem
        else:
            temp = BeautifulSoup('<body>', 'html.parser').find("body")
            temp.append(aitem)
            body = temp
    elif is_results(aitem):
        temp = BeautifulSoup('<body>', 'html.parser').find("body")
        for btag in aitem:
            temp.append(btag)
        body = temp
    else:
        body = None
    return body


def unpack_hrefs(tag):
    """ Unpacks the href links from all a tags, and append the links as a string tag
        The function changes the existing tag

        Args:
            tag (tag): BS4 tag

        Returns:
        """
    results = tag.find_all('a')
    results.append(tag)

    for atag in results:
        if 'href' in atag.attrs:
            astr = '<span>' + str(atag["href"]) + '</span>'
            htag = BeautifulSoup(astr, 'html.parser').find("span")
            atag.append(htag)


def remove_navigable_strings(results):
    """ Remove navigable strings from ResultSet
    The function removes list item of type Navigable String.
    Tag items which contain navigable strings are not removed.

    results = remove_navigable_strings(results)

    Args:
        results (ResultSet): BS4 ResultSet

    Returns:
        results (ResultSet): BS4 ResultSet
    """
    for aitem in reversed(results):
        if is_navigable_string(aitem):
            results.remove(aitem)
    return results


def wrap_navigable_strings(tag, empty=False):
    """ Wrap navigable strings into tags
    The function wraps navigable string into a span tag if the navigable string
    is not the only child of a tag.
    The function changes the existing tag

        wrap_navigable_strings(tag)

    Args:
        tag (tag): BS4 tag
        empty (bool): Wrap empty strings if True

    Returns:
    """
    new_tags = []
    for aitem in tag.descendants:
        if is_navigable_string(aitem) and not aitem.parent.string:
            if empty or (aitem.string is not None and aitem.string != '\n'):
                new_tag = tag.new_tag("span")
                aitem.wrap(new_tag)
                new_tags.append(new_tag)

    # Strip new tags
    for aitem in new_tags:
        _ = aitem.string.replace_with(aitem.string.strip())


# I/O functions
def read(filename):
    """ Read page from file

        page = read(filename)

        Args:
            filename (str): file name of HTML page

        Returns:
            page(str)
    """

    page = utils.read(filename)
    return page


def write(filename, page):
    """ Write HTML page to file

            write(filename, page)

            Args:
                filename (str): file name
                page (str): HTML page

            Returns:
                None

            Raises:
                IOError (): error in case function cannot write to filename
        """

    utils.write(filename, page)


# Search functions
def find_soup(aitem):
    """ Find soup of aitem

    asoup = find_soupd(aitem)

    Args:
        aitem(tag or soup): BS4 object

    Returns:
        asoup (soup): BS4 soup object
    """
    asoup = None
    if is_soup(aitem):
        asoup = aitem
    elif is_tag(aitem):
        rlist = list(reversed(list(aitem.parents)))
        asoup = rlist[0]
    return asoup


def find_items(aitem, afilter=None, astr=''):
    """ Find items from aitem based on filter and/or string

    ritems = find_items(aitem, filter=afilter, astr='')

    Args:
        aitem(soup or tag or ResultSet): BS4 object
        afilter (dict): BS4 filter
        astr (str): string or regular expression for filter on aitem.string

    Returns:
        ritems (ResultSet): BS4 resultset
    """

    afilter = {} if afilter is None else afilter
    has_item = "elem" in afilter
    has_class = "class" in afilter

    if has_item and has_class:
        class_ = ' '.join(afilter["class"])
        ritems = aitem.find_all(afilter["elem"], class_=class_, string=astr)
    elif has_item and not has_class:
        ritems = aitem.find_all(afilter["elem"], string=astr)
    elif not has_item and has_class:
        class_ = ' '.join(afilter["class"])
        ritems = aitem.find_all(class_=class_, string=astr)
    else:
        ritems = aitem.find_all(True, string=astr)
    return ritems


def find_item(aitem, afilter=None, astr=''):
    """ Find single item from aitem based on filter and/or string

    ritem = find_item(aitem, filter=afilter, astr='')

    Args:
        aitem(soup or tag or ResultSet): BS4 object
        afilter (dict): BS4 filter
        astr (str): string or regular expressiom for filter on aitem.string

    Returns:
        ritem (tag): BS4 tag
    """

    afilter = {} if afilter is None else afilter
    has_item = "elem" in afilter
    has_class = "class" in afilter

    if has_item and has_class:
        class_ = ' '.join(afilter["class"])
        ritem = aitem.find(afilter["elem"], class_=class_, string=astr)
    elif has_item and not has_class:
        ritem = aitem.find(afilter["elem"], string=astr)
    elif not has_item and has_class:
        class_ = ' '.join(afilter["class"])
        ritem = aitem.find(class_=class_, string=astr)
    else:
        ritem = aitem.find(True, string=astr)
    return ritem


def find_item_by_xpath(aitem, axpath='', relative=True):
    """ Find single item from aitem based on xpath

    ritem = find_item_by_xpath(aitem, xpath=xpath)

    Args:
        aitem(tag): BS4 object
        axpath (str): xpath
        relative (bool): xpath is relative to aitem if true, absolute otherwise

    Returns:
        ritem (tag): BS4 tag
    """

    if not relative:
        asoup = find_soup(aitem)
        ritem = find_item_by_xpath(asoup, axpath=axpath, relative=True) if is_soup(asoup) else None
    else:
        [names, idx] = xsplit(axpath)
        tf = True
        ritem = aitem
        # Iterate over xpath items and update ritem each step
        while tf:
            if len(names) == 0:
                tf = False
            else:
                names_i = names.pop(0)
                idx_i = idx.pop(0)
                if idx_i == 1:
                    ritem = ritem.find(names_i)
                    if ritem is None:
                        tf = False
                else:
                    next_items = ritem.find_all(names_i)
                    if len(next_items) >= idx_i:
                        ritem = next_items[idx_i-1]
                    else:
                        ritem = None
                        tf = False
    return ritem


def find_lists(aitem, afilter=None, astr=''):
    """ Find all lists in aitem. Lists are defined as HTML elements <dl>, <ol>, or <ul>

    ritems = find_lists(aitems)

    Args:
        aitem(soup or tag or ResultSet): BS4 object
        afilter (dict): BS4 filter
        astr (str): string or regular expressiom for filter on aitem.string

    Returns:
        ritems (ResultSet): BS4 resultset
    """

    afilter = {} if afilter is None else afilter
    afilter.update({"elem": ["dl", "ol", "ul"]})
    ritems = find_items(aitem, afilter=afilter, astr=astr)
    return ritems


def find_tables(aitem, afilter=None, astr=''):
    """ Find all tables in aitem. Tables are defined as HTML elements <table>

    ritems = find_tables(aitems)

    Args:
        aitem(soup or tag or ResultSet): BS4 object
        afilter (dict): BS4 filter
        astr (str): string or regular expressiom for filter on aitem.string

    Returns:
        ritems (ResultSet): BS4 resultset
    """

    afilter = {} if afilter is None else afilter
    afilter.update({"elem": ["table"]})
    ritems = find_items(aitem, afilter=afilter, astr=astr)
    return ritems


def get_filter(aitem):
    """ Get filter for aitem

    afilter = get_filter(aitem)

    Args:
        aitem(tag): BS4 object

    Returns:
        afilter (dict): dict with keys 'elem' and 'class'
    """
    afilter = {'elem': '', 'class': ['']}
    if is_tag(aitem):
        afilter['elem'] = aitem.name
        afilter['class'] = aitem['class'] if 'class' in aitem.attrs else ['']
    return afilter


def get_filters(aitems):
    """ Get filter for aitem

    alist = get_filters(aitem)

    Args:
        aitems(tag or resultset): BS4 object

    Returns:
        alist(list): List of filters
    """
    aresults = aitems if isinstance(aitems, list) else [aitems]
    return [get_filter(aitem) for aitem in aresults]


def get_filter_most_common(afilters):
    """ Get filter most common returns the filter with most occurences

        afilter = get_filter_most_common(afilters)

        Args:
            afilters (list): List of BS4 filters (dict)

        Returns:
            afilter (dict): dict with keys 'elem' and 'class'
    """
    jfilters = dicts.dumps(afilters)
    coll = collections.Counter(jfilters)
    alist = coll.most_common(1)
    tup = alist[0]
    afilter = dicts.loads(tup[0])
    return afilter


def remove_filters(afilters, elem=None, class_=None):
    """ Remove filter from afilters based on elem and/or class_

        afilters = _remove_filters(afilters, elem=None,class_=None)

        Args:
            afilters(list): list of filters
            elem (str):
            class_ (str or list):
        Returns:
            afilters(list): list of filters

    """
    for afilter in afilters[:]:  # [:] creates a copy
        do_remove = afilter['elem'] == elem if elem is not None else False
        do_remove = do_remove or (afilter['class'] == class_ if class_ is not None else False)
        if do_remove:
            afilters.remove(afilter)
    return afilters


# Tree functions
def common_ancestor(aitem1, aitem2):
    """ Find tag whose descendants contain both aitem1 and aitem2

    ritem = common_ancestor(aitem1, aitem2)

    Args:
        aitem1 (tag): BS4 tag
        aitem2 (tag): BS4 tag

    Returns:
        ritem (tag): BS4 tag
    """

    aitem = None
    if is_tag(aitem1) and is_tag(aitem2):
        parents1 = list(reversed(list(aitem1.parents)))
        parents2 = list(reversed(list(aitem2.parents)))
        for p1, p2 in zip(parents1, parents2):
            if p1 == p2:
                aitem = p1
    return aitem


def common_ancestors(aitems1, aitems2):
    """ Return a list of common ancestor for all combinations in aitems1 and aitems2

    ritem = common_ancestor(aitem1, aitem2)

    Args:
        aitems1 (tag or Resultset): BS4 tag
        aitems2 (tag or Resultset): BS4 tag

    Returns:
        ritems (list): List of common ancestors
    """
    aresults1 = aitems1 if isinstance(aitems1, list) else [aitems1]
    aresults2 = aitems2 if isinstance(aitems2, list) else [aitems2]

    return [common_ancestor(aitem1, aitem2) for aitem1 in aresults1 for aitem2 in aresults2]


def ancestors(aitem):
    """ Find all ancestor tags on direct line between soup and aitem (exclude both)
       Returns an ordered list of tags

       rlist = ancestors(aitem)

       Args:
           aitem (tag): BS4 tag

       Returns:
           rlist (list): List of BS4 tag
       """
    alist = list(reversed(list(aitem.parents)))
    if is_soup(alist[0]):
        alist.pop(0)
    return alist


def children(aitem, include_navs=False):
    """ Find all children of aitem
    Returns an ordered list of tags

    rlist = children(aitem, include_navs=False)

    Args:
       aitem (tag): BS4 tag
       include_navs (bool): Include navstrings if True

    Returns:
       rlist (list): List of BS4 tag
    """
    rlist = []
    if is_tag(aitem):
        rlist = [citem for citem in aitem.children if is_tag(citem) or include_navs]
    return rlist


def lineage(aancestor, adescendant):
    """ Find all tags on direct line of descent between ancestor and descendant (exclude both)
    Returns an ordered list of tags

    rlist = lineage(aancestor, adescendant)

    Args:
        aancestor (tag): BS4 tag
        adescendant (tag): BS4 tag

    Returns:
        rlist (list): List of BS4 tags
    """
    rlist = ancestors(adescendant)
    tf = False
    while not tf and len(rlist) > 0:
        curr_parent = rlist.pop(0)
        tf = (curr_parent == aancestor)
    return rlist


def position(aitem, include_navs=False):
    """ Position of aitem in children list of parent

    idx = position(aitem, include_navs=False)

    Args:
       aitem (tag): BS4 tag
       include_navs (bool): Include navstrings if True

    Returns:
       idx (int): index of aitem in children of aparent
    """
    idx = None
    if is_tag(aitem) and not is_soup(aitem):
        aparent = aitem.parent
        achildren = children(aparent, include_navs=include_navs)
        idx = achildren.index(aitem)
    return idx


def get_child_of_common_ancestor(aitem1, aitem2):
    """ Get first child of common ancestor.

        achild = get_child_of_common_ancestor(soup, aitem1, aitem2)

        Args:
            aitem1 (tag): BS4 object
            aitem2 (tag): BS4 object

        Returns:
            achild (tag): First child of common ancestor
    """
    aitem = None

    aparent = common_ancestor(aitem1, aitem2)
    if aparent:
        alineage = lineage(aparent, aitem1)
        aitem = alineage[0] if alineage else aitem1
    return aitem


def get_child_of_common_ancestors(aitems1, aitems2):
    """ Get first child of common ancestor.
        Returns a list with all combinations of aitem1 and aitems2.

        alist = get_child_of_common_ancestor(soup, aitem1, aitem2)

        Args:
            aitems1 (list): List of BS4 tags
            aitems2 (list): List of BS4 tags

        Returns:
            alist (list): List with first child of common ancestor
    """
    aresults1 = aitems1 if isinstance(aitems1, list) else [aitems1]
    aresults2 = aitems2 if isinstance(aitems2, list) else [aitems2]

    return [get_child_of_common_ancestor(aitem1, aitem2) for aitem1 in aresults1 for aitem2 in aresults2]


def get_ancestor_unique_filter(aitem):
    """ Get first ancestor of aitem which has a unique filter in soup

        aancestor = get_ancestor_unique_filter(aitem)

        Args:
            aitem (tag): BS4 object

        Returns:
            aancestor (tag): BS4 object
    """
    aancestors = ancestors(aitem)
    aancestor = None
    is_unique = False
    soup = find_soup(aitem)

    while not is_unique and len(aancestors) > 0:
        aancestor = aancestors.pop()
        afilter = get_filter(aancestor)
        is_unique = is_unique_filter(afilter, soup)
    return aancestor


def get_ancestors_unique_filter(aitems):
    """ Get first ancestor of aitem which has a unique filter in soup

        aancestors = get_ancestors_unique_filter(aitems)

        Args:
            aitems (list): BS4 object

        Returns:
            aancestors (list): BS4 object
    """
    aresults = aitems if isinstance(aitems, list) else [aitems]
    return [get_ancestor_unique_filter(aitem) for aitem in aresults]


def get_parents(aitems):
    """ Get parent for each item in aitems

         aparents = get_parents(aitems)

         Args:
             aitems (list): List of BS4 tags

         Returns:
             aparents (list): List of BS4 tags
     """
    return [aitem.parent for aitem in aitems]


# Text extraction functions
def get_text(aitem, cols=None, include_strings=True, include_links=False, fill_missing_cols=True):
    """ Get text from soup objects. Text consists of strings and/or links.
        Returns all text of descendant items if no columns are specified, or
        text of specific columns only, if columns are specified.

    alist = get_text(aitem, cols=cols, include_strings=True, include_links=False)

    Args:
        aitem(soup or tag or ResultSet): BS4 object
        cols (str or list): string or list of dicts with keys {'elem','class'}
        include_strings (boolean): Include strings if true
        include_links (boolean): Include links if true
        fill_missing_cols (boolean): Fill missing columns if true

    Returns:
        alist (list): List of strings (tag) or list of list of strings (ResultSet)
    """
    alist = []

    if is_tag(aitem):
        aitem = [aitem]
        do_unpack = True
    else:
        do_unpack = False

    for atag in aitem:
        do_flatten = False

        # Get string item
        if isinstance(cols, list):
            sitem = _get_cols_as_results(atag, cols, fill_missing_cols=fill_missing_cols)
            do_flatten = True
        elif isinstance(cols, str):
            # TODO stencil
            sitem = atag
            # TODO Convert list to Resultset. See get_subtext
        else:
            sitem = atag

        # Extract text
        if include_strings:
            alist_item = get_strings(sitem, include_links=include_links)
        elif include_links:
            alist_item = get_links(sitem)
        else:
            alist_item = []

        # Flatten text
        if do_flatten:
            alist_item = [[''] if lists.is_empty(val) else val for val in alist_item]
            alist_item = lists.flatten(alist_item)

        alist.append(alist_item)

    if do_unpack:
        alist = alist[0]
    return alist


def get_strings(aitem, include_links=False):
    """ Get strings from soup objects

    alist = get_strings(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object
        include_links (boolean): Include links as strings if true

    Returns:
        alist (list): List of strings (soup or tag) or list of list of strings (ResultSet)
    """
    alist = []
    if is_tag(aitem):
        alist = _get_strings_from_tag(aitem, include_links)
    elif is_results(aitem):
        alist = _get_strings_from_results(aitem, include_links)
    return alist


def get_links(aitem):
    """ Get links from soup objects

    alist = get_links(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object

    Returns:
        alist (list): List of strings (soup or tag) or list of list of strings (ResultSet)
    """
    alist = []
    if is_tag(aitem) or is_soup(aitem):
        alist = _get_links_from_tag(aitem)
    elif is_results(aitem):
        alist = _get_links_from_results(aitem)
    return alist


# Stencil functions

# A stencil provides a tag with mask layout filled with strings and links content from aitem.
# A mask consists of a bs4 structure without content


def stencil(aitem, amask):
    """ Get stencil from soup or tag
    # A stencil returns tag sitem with mask layout filled with strings and links content from aitem.

    sitem = stencil(aitem, amask)

    Args:
        aitem : soup or tag
        amask : tag

    Returns:
        sitem : tag
    """

    # TODO

    # 1. Copy aitem to sitem
    sitem = copy.copy(aitem)

    xd_item = xpaths(sitem, root=sitem, first_index=True)
    xd_mask = xpaths(amask, root=amask, first_index=True)

    # 2. Find all tags in sitem not in amask and delete these tags from aitem
    xpaths_redundant = xpaths_set(xd_item, xd_mask, operation='difference', relative=True)
    for ax in xpaths_redundant:
        ritem = find_item_by_xpath(sitem, axpath=ax, relative=True)
        ritem.decompose() if ritem else None

    # 3. Find all tags in atemplate not in aitem and add in correct position with ''
    xpaths_missing = xpaths_set(xd_mask, xd_item, operation='difference', relative=True)
    for ax in xpaths_missing:
        ditem = find_item_by_xpath(amask, axpath=ax, relative=True)
        idx = position(ditem, include_navs=True)

        nitem = copy.copy(ditem)

        # TODO

        # Get elem
        # Create tag
        # Fill content of tag
        pass

    return sitem


def get_mask(aitem, astr='', ahref=''):
    """ Get Mask from soup or tag
    A mask consists of a bs4 structure without content
    Navigable strings and hrefs values are replaced
    All other attributes, except class, are stripped

    ritem = get_mask(aitem)

    Args:
        aitem : soup or tag
        astr  : filling string or 'count'
        ahref : filling href

    Returns:

        ritem : soup or tag
    """

    ritem = None
    if is_tag(aitem) or is_soup(aitem):
        ritem = copy.copy(aitem)

        # strings
        results = ritem.find_all(text=True)
        for i, atag in enumerate(results):
            rstr = str(i) if astr == 'count' else astr
            _ = atag.string.string.replace_with(rstr)

        # hrefs
        results = ritem.find_all('a')
        results.append(ritem)
        for atag in results:
            if 'href' in atag.attrs:
                atag['href'] = ahref

        # Other attributes
        results = ritem.find_all()
        for atag in results:
            for att in atag.attrs:
                if att not in ('class', 'href'):
                    atag[att] = ''

    return ritem


# Identification functions
def is_tag(aitem):
    """ Returns true if aitem is bs4.element.Tag

    tf = is_tag(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object

    Returns:
        tf (bool): True if aitem is BS4 tag, False otherwise
    """
    return isinstance(aitem, bs4.element.Tag)


def is_results(aitem):
    """ Returns true if aitem is bs4.element.ResultSet

    tf = is_results(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object

    Returns:
        tf (bool): True if aitem is BS4 Resultset, False otherwise
    """
    return isinstance(aitem, bs4.element.ResultSet)


def is_soup(aitem):
    """ Returns true if aitem is bs4.BeautifulSoup

    tf = is_soup(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object

    Returns:
        tf (bool): True if aitem is BS4 soup, False otherwise
    """
    return isinstance(aitem, bs4.BeautifulSoup)


def is_navigable_string(aitem):
    """ Returns true if aitem is BS4 NavigableString

    tf = is_navigable_string(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object

    Returns:
        tf (bool): True if aitem is BS4 Navigable String, False otherwise
    """
    return isinstance(aitem, bs4.element.NavigableString)


def is_leaf(aitem):
    """ Returns true if aitem is a leaf bs4.element.Tag.

    tf = is_leaf(aitem)

    Args:
        aitem(soup or tag or ResultSet): BS4 object

    Returns:
        tf (bool): True if aitem is leaf BS4 tag, False otherwise
    """
    return is_tag(aitem) and is_navigable_string(aitem.next)


def is_empty_filter(afilter):
    """ True if filter is empty

    tf = is_empty_filter(afilter)

    Args:
        afilter (dict): BS4 filter

    Returns:
        tf: True if filter is empty
    """
    return lists.is_empty(afilter['elem']) and lists.is_empty(afilter['class'])


def is_filter(afilter):
    """ Returns true if afilter is a filter

    tf = is_filter(afilter)

    Args:
        afilter (dict): dict with keys 'elem' and 'class' (if True)

    Returns:
        tf (bool): True if afilter is filter, False otherwise
    """
    return isinstance(afilter, dict) and ('elem' in afilter and 'class' in afilter)


def is_unique_filter(afilter, aitem):
    """ Returns true if afilter is unique in aitem

        tf = is_unique_filter(afilter, aitem)

        Args:
            afilter (dict): dict with keys 'elem' and 'class' (if True)
            aitem(tag or soup): BS4 object

        Returns:
            tf (bool): True if afilter is unique filter in aitem, False otherwise
    """
    tf = is_filter(afilter) and (is_tag(aitem) or is_soup(aitem))
    if tf:
        results = find_items(aitem, afilter=afilter)
        tf = len(results) == 1
    return tf


# Xpath functions
def xpath(aitem, root=None, first_index=False):
    """ Returns xpath of aitem.
    Returns absolute path or relative path to root

    xpath = xpath(aitem, root, first_index)

    Args:
        aitem(tag): BS4 object
        root(tag): BS4 tag (optional)
        first_index(bool): include first index if true

    Returns:
        axpath (str or list): xpath of aitem
    """
    axpath = ''
    if is_tag(aitem) and not is_soup(aitem):
        if aitem == root:
            axpath = '//'
        else:
            # Absolute
            rlist = ancestors(aitem)
            rlist.append(aitem)
            for aparent in rlist:
                idx = _get_xpath_index(aparent, first_index=first_index)
                sidx = '[' + str(idx) + ']' if idx > 0 else ''
                axpath = axpath + '/' + aparent.name + sidx

            # Relative
            if is_tag(root):
                axpath_root = xpath(root, first_index=first_index)
                axpath = axpath.replace(axpath_root, '/') if axpath.startswith(axpath_root) else ''
    return axpath


# Xpaths. Xpath set functions.
def xpaths(aitem, root=None, first_index=False):
    """ Returns list of xpaths of all descendant tags

    alist = xpaths(aitem, root, first_index)

    Args:
        aitem(tag): BS4 object
        root(tag): BS4 tag (optional)
        first_index(bool): include first index if true

    Returns:
        alist (list): xpaths of all descendant tags
    """
    alist = []
    if is_tag(aitem):
        # if not is_soup(aitem):
        #     alist.append(xpath(aitem, root=root))
        for atag in aitem.descendants:
            if is_tag(atag):
                alist.append(xpath(atag, root=root, first_index=first_index))
    return alist


def xpaths_set(aitem1, aitem2, operation=None, relative=False):
    """ Returns an unordered list with set operation on xpaths in aitem1 and aitem2
     When relative is true relative xpaths are relative to root of aitem1 and aitem2

    alist = xpaths_set(aitem1, aitem2)

    Args:
        aitem1(tag): BS4 object
        aitem2(tag): BS4 object
        operation(str): 'union', 'intersect' or 'difference'
        relative (bool): Abolute (False) or relative (True)

    Returns:
        alist (list): list with xpaths from of aitem1 and aitem2 based on operation
    """

    xpath1 = xpaths(aitem1, root=(aitem1 if relative else None), first_index=True)
    xpath2 = xpaths(aitem2, root=(aitem2 if relative else None), first_index=True)

    if operation == 'union':
        alist = lists.union(xpath1, xpath2)
    elif operation == 'intersect':
        alist = lists.intersect(xpath1, xpath2)
    elif operation == 'difference':
        alist = lists.difference(xpath1, xpath2)
    else:
        alist = []
    return alist


# Private xpath functions
def _get_xpath_index(aitem, first_index=False):
    """ Returns xpath index. A positive index represents k-th index
    A zero index represents first index with no further occurences of same name

    xpi = _get_xpath_index(aitem, first_index)

    Args:
        aitem(tag): BS4 object
        first_index(bool): include first index if true

    Returns:
        xpi (int): xpath index of aitem
    """
    xpi = 0
    if is_tag(aitem) and not is_soup(aitem):
        aname = aitem.name
        nitems = 0
        aparent = next(aitem.parents)
        for citem in aparent.children:
            if is_tag(citem):
                if citem.name == aname:
                    nitems = nitems + 1
                    if citem == aitem:
                        xpi = nitems
        xpi = xpi if (nitems > 1 or first_index) else 0
    return xpi


# Private functions
def _get_colnames(ncols):
    """ Get column names

        [colnames] = _get_colnames(nitems)

        Args:
            ncols (int): Number of colums
        Returns:
            acolnames (list): Column names
        """
    return ['Col' + str(i + 1) for i in range(ncols)]


def _get_cols_as_results(aitem, cols, fill_missing_cols=True):
    """ Get columns as a Resultset

        aresults = _get_cols_as_results(aitem)

        Args:
            aitem(soup or tag or ResultSet): BS4 object
            cols (list): list of dicts with keys {'elem','class'}
            fill_missing_cols (boolean): Fill missing columns if true

        Returns:
            aresults (ResultSet): ResultSet
        """
    if not is_results(aitem):
        aitem = [aitem]

    # Create empty ResultSet
    aresults = aitem[0].find_all("")

    if fill_missing_cols:
        asoup = find_soup(aitem[0])
        stag = asoup.new_tag('i')
        ltag = asoup.new_tag('a', href='')
    else:
        stag = None
        ltag = None

    for record in aitem:
        for col in cols:
            atag = find_item(record, col)
            if is_tag(atag):
                aresults.append(atag)
            elif fill_missing_cols:
                if col['elem'] == 'a':
                    aresults.append(ltag)
                else:
                    aresults.append(stag)
    return aresults


def _get_strings_from_results(results, include_links=False):
    """ Get strings from results

    alist = _get_strings_from_results(results)

    Args:
        results (ResultSet): BS4 result set
        include_links (boolean): Include hrefs as strings if true

    Returns:
        alist (list): List of strings
    """
    return [_get_strings_from_tag(tag, include_links) for tag in results]


def _get_links_from_results(results):
    """ Get links from results. Links are href strings

    alist = _get_links_from_results(results)

    Args:
        results (ResultSet): BS4 result set

    Returns:
        alist (list): List of links
    """
    return [_get_links_from_tag(tag) for tag in results]


def _get_strings_from_tag(tag, include_links=False):
    """ Get strings from tag

    alist = _get_strings_from_tag(tag)

    Args:
        tag (tag): BS4 tag
        include_links (boolean): Include links if true

    Returns:
        alist (list): List of strings
    """
    if include_links:
        atag = copy.copy(tag)
        unpack_hrefs(atag)
    else:
        atag = tag
    return [text for text in atag.stripped_strings]


def _get_links_from_tag(tag):
    """ Get links from tag. Links are href strings

    alist = _get_links_from_tag(tag)

    Args:
        tag (tag): BS4 tag

    Returns:
        alist (list): List of links
    """
    results = tag.find_all('a')
    results.append(tag)
    alist = [tag['href'] if 'href' in tag.attrs else None for tag in results]
    alist = list(filter(None, alist))
    return alist
