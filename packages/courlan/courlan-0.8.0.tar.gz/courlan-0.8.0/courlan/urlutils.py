"""
Functions related to URL manipulation and extraction of URL parts.
"""

import re

from functools import lru_cache
from urllib.parse import urlparse, ParseResult

from tld import get_tld


DOMAIN_REGEX = re.compile(r'(?:http|ftp)s?://(?:www[0-9]*\.)?([^/]+)')
NO_EXTENSION_REGEX = re.compile(r'(^[^.]+)')
CLEAN_DOMAIN_REGEX = re.compile(r'^www[0-9]*\.')


@lru_cache(maxsize=1024)
def get_tldinfo(url, fast=False):
    '''Cached function to extract top-level domain info'''
    if fast is True:
        # try with regexes
        match = DOMAIN_REGEX.match(url)
        if match:
            full_domain = match.group(1)
            return NO_EXTENSION_REGEX.match(full_domain).group(0), full_domain
    # fallback
    tldinfo = get_tld(url, as_object=True, fail_silently=True)
    if tldinfo is None:
        return None, None
    # this step is necessary to standardize output
    return tldinfo.domain, CLEAN_DOMAIN_REGEX.sub('', tldinfo.fld)


def extract_domain(url, blacklist=None, fast=False):
    '''Extract domain name information using top-level domain info'''
    if blacklist is None:
        blacklist = set()
    # new code: Python >= 3.6 with tld module
    domain, full_domain = get_tldinfo(url, fast=fast)
    # invalid input
    if full_domain is None:
        return None
    # blacklisting
    if domain in blacklist or full_domain in blacklist:
        return None
    # return domain
    return full_domain


def _parse(url):
    'Parse a string or use urllib.parse object directly.'
    if isinstance(url, str):
        parsed_url = urlparse(url)
    elif isinstance(url, ParseResult):
        parsed_url = url
    else:
        raise TypeError('wrong input type:', type(url))
    return parsed_url


def get_base_url(url):
    '''Strip URL of some of its parts to get base URL.
       Accepts strings and urllib.parse ParseResult objects.'''
    parsed_url = _parse(url)
    return parsed_url._replace(path='', params='', query='', fragment='').geturl()


def get_host_and_path(url):
    '''Decompose URL in two parts: protocol + host/domain and path.
       Accepts strings and urllib.parse ParseResult objects.'''
    parsed_url = _parse(url)
    host = parsed_url._replace(path='', params='', query='', fragment='')
    path = parsed_url._replace(scheme='', netloc='')
    hostval, pathval = host.geturl(), path.geturl()
    # correction for root/homepage
    if pathval == '':
        pathval = '/'
    if not hostval or not pathval:
        raise ValueError('incomplete URL: %s', url)
    return hostval, pathval


def get_hostinfo(url):
    'Extract domain and host info (protocol + host/domain) from a URL.'
    domainname = extract_domain(url, fast=True)
    parsed_url = urlparse(url)
    host = parsed_url._replace(path='', params='', query='', fragment='')
    return domainname, host.geturl()


def fix_relative_urls(baseurl, url):
    'Prepend protocol and host information to relative links.'
    if url.startswith('//'):
        return 'https:' + url if baseurl.startswith('https') else 'http:' + url
    if url.startswith('/'):
        # imperfect path handling
        return baseurl + url
    if url.startswith('.'):
        # don't try to correct these URLs
        return baseurl + '/' + re.sub(r'(.+/)+', '', url)
    if not url.startswith('http') and not url.startswith('{'):
        return baseurl + '/' + url
    # todo: handle here
    #if url.startswith('{'):
    return url


def is_external(url, reference, ignore_suffix=True):
    '''Determine if a link leads to another host, takes a reference URL and
       a URL as input, returns a boolean'''
    stripped_ref, ref = get_tldinfo(reference, fast=True)
    stripped_domain, domain = get_tldinfo(url, fast=True)
    # comparison
    if ignore_suffix is True:
        return stripped_domain != stripped_ref
    return domain != ref


def is_known_link(link, known_links):
    "Compare the link and its possible variants to the existing URL base."
    # easy check
    if link in known_links:
        return True
    # trailing slash
    test1 = link.rstrip('/')
    test2 = test1 + '/'
    if test1 in known_links or test2 in known_links:
        return True
    # http/https + trailing slash
    if link[:4] == 'http':
        if link[:5] == 'https':
            testlink = link[:4] + link[5:]
        else:
            testlink = ''.join([link[:4], 's', link[4:]])
        test1, test2 = testlink.rstrip('/'), testlink.rstrip('/') + '/'
        return testlink in known_links or test1 in known_links or test2 in known_links
    return False
