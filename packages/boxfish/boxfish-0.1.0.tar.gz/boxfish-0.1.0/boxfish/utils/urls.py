# urls.py

""" urls contains functions to parse url strings """

from urllib.parse import parse_qsl, urlencode, urlsplit, urljoin
from boxfish.utils.dicts import get_subset, remove_nones
from boxfish.utils.lists import reshape


def set_components(url, **kwargs):
    """ Set url components based on dict or key value pairs

    url = set_components(url, scheme=scheme, netloc=netloc, path=path, query=query, fragment=fragment)

    Args:
        url (str) : url
        **kwargs: # url components
            scheme (str): Scheme
            netloc (str): Netloc
            path (str): Path
            query (str or dict): Query
            fragment (str or dict): Fragment
    Returns:
        url (str)
    """

    kwargs = get_subset(remove_nones(kwargs), ['scheme', 'netloc', 'path', 'query', 'fragment'])
    if 'query' in kwargs:
        kwargs['query'] = _dict_to_query(kwargs['query']) if isinstance(kwargs['query'], dict) else kwargs['query']

    pr = urlsplit(url)
    pr = pr._replace(**kwargs)
    url = pr.geturl()
    return url


def get_components(url):
    """ Set url components based on dict or key value pairs

    url = set(url, query=query, path=path, )

    Args:
        url (str) : url
    Returns:
        components (dict)
            scheme (str): Scheme
            netloc (str): Netloc
            path (str): Path
            query (str): Query
            fragment (str): Fragment
    """
    pr = urlsplit(url)
    components = dict()
    components['scheme'] = pr.scheme
    components['netloc'] = pr.netloc
    components['path'] = pr.path
    components['query'] = pr.query
    components['fragment'] = pr.fragment
    return components


def replace_subpath(url, subpath, index):
    """ Replace subpath replaces a single subpath of the path of an url

    url = replace_subpath(url, subpath, index=0)

    Args:
        url (str) : url
        subpath (str): subpath
        index (int): index of path between 0 and n-1 or between -1 and -n
    Returns:
        aurl (str) : url
    """

    aurl = url
    adict = get_components(url)
    dictpath = _path_to_dict(adict['path'])
    keys = list(dictpath.keys())

    if len(keys)==0:
        aurl = set_components(url, path=subpath)
    else:
        if -len(keys) <= index < len(keys):
            dictpath[keys[index]] = subpath
            aurl = set_components(url, path=_dict_to_path(dictpath))
    return aurl


def replace_subquery(url, subquery):
    """ Replace subquery replaces part of a query of an url

    url = replace_subquery(url, subquery)

    Args:
        url (str) : url
        subquery (str or dict): sub query
    Returns:
        aurl (str) : url
    """

    adict = get_components(url)
    dictquery = _query_to_dict(adict['query'])
    dictsubquery = _query_to_dict(subquery) if isinstance(subquery, str) else subquery

    dictquery = dict(dictquery, **dictsubquery)
    aurl = set_components(url, query=_dict_to_query(dictquery))
    return aurl


def update_relative_path(url, newpath):
    """ Update url with a relative newpath.
    Existing path and query are overwritten by newpath

    url = update_path(url, newpath)

    Args:
        url (str) : url
        newpath (str): subpath
    Returns:
        aurl (str) : url
    """
    aurl = urljoin(url,newpath)
    return aurl


def create_url_list(url, query=None, path=None):
    """ Create a list of urls based on a url, a query and/or path

    url_list = create_url_list(url, query=query, path=path)

    Args:
        url (str) : url
        query (str or list): Query list
        path (str or list): Path list
    Returns:
        url_list (list) : url list
    """
    url_list = []
    [url, query, path] = reshape(url, query, path)
    if url is not None:
        for index in range(len(url)):
            url_i = set_components(url[index], query=query[index], path=path[index])
            url_list.append(url_i)
    return url_list


def is_valid_http(url):
    """ Validate url syntax for http and https

    url = valid(url)

    Args:
        url (str) : url
    Returns:
        tf (bool) : True if url is a valid url
    """
    pr = urlsplit(url)
    return (pr.scheme == 'http') or (pr.scheme == 'https')


# Private functions
def _dict_to_path(adict):
    """ Convert a dict to a url path

        path = _dict_to_path(adict)

        Args:
            adict (dict): key-value pairs

        Returns:
            path (str): url path /value1/value2 based on values in adict
    """
    path = ''
    if type(adict) == dict:
        for value in adict.values():
            path = path + '/' + value.lstrip('/')
    return path


def _path_to_dict(path, keys=None):
    """ Convert a url path to a dict

        adict = _path_to_dict(path, keys=None)

        Args:
            path (str): url path /value1/value2
            keys (list): list of key strings or None

        Returns:
            adict (dict): key-value pairs for each element in path
    """
    adict = {}
    if type(path) == str:
        values = list(filter(None, path.split('/')))
        elems = len(values)

        if keys is None:
            keys = ["{}".format(i) for i in range(elems)]
        if len(keys) == elems:
            for i in range(elems):
                adict[keys[i]] = values[i]
    return adict


def _query_to_dict(query):
    return dict(parse_qsl(query))


def _dict_to_query(adict):
    return urlencode(adict)
