#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:13 PM
import os
import re
import sys
import json
import shutil
import warnings
import logging

import six
import requests
from requests.packages.urllib3 import exceptions
from bunch import Bunch

if six.PY2:
    import urlparse as uparse
elif six.PY3:
    import urllib.parse as uparse
else:
    raise EnvironmentError('Unknown python major version.')

VERB_SWAPS = {
    'GET': '',
    'POST': 'set',
    'DELETE': 'del',
    'PUT': 'put'
}

MIN_TIMEOUT_SECS = 0.5
DEFAULT_CACHE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs')
API_FILENAME = 'api_%s.md'

def get_latest_documentation(
        url = None,
        as_version = None,
        cache_folder = DEFAULT_CACHE_FOLDER):

    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    cachefile = os.path.join(cache_folder, API_FILENAME % 'latest' if not as_version else as_version)

    if os.path.exists(cachefile):
        shutil.copyfile(cachefile, cachefile + '_old')

    if url is None:
        url = r'https://github.com/syncthing/docs/tree/gh-pages/_rest'

    print('Getting latest documentation..')

    build_out = ''
    raw_page_prefix = 'https://raw.githubusercontent.com'
    stub_regex = re.compile(r'href=\"(?P<doc_url>/syncthing/docs/blob/gh-pages/_rest/(?P<doc_name>\S+)\.md)\"', re.I)
    page_html = requests.get(url).text

    for fullpath, filename in stub_regex.findall(page_html):
        print('...grabbing: ' + filename)

        fname = filename.split('-')
        markdown_page = raw_page_prefix + fullpath.replace('/blob', '')

        # get the markdown data from the github url
        resp = requests.get(markdown_page).text

        build_out += '''
### {verb} {endpoint}

{raw}
        '''.format(
            verb = fname[-1].upper(),
            endpoint = 'rest/' + '/'.join(fname[0:-1]),
            raw = resp.strip()).strip()


    with open(cachefile, 'w') as out_file:
        out_file.write(build_out)
    return cachefile

class Interface(object):
    """HTTP Interface for the Syncthing REST protocol.

    Handles SSL and POST headers for every request made from the
    syncthing.Syncthing class.
    """
    def __init__(self,
            api_key,               # found in Syncthing settings for target node
            host = 'localhost',    # the hostname or IP for the target node
            port = 8080,           # Syncthing application port
            timeout = 3.0,         # REST request timeout limit, in seconds
            is_https = False,      # http or https protocol
            ssl_cert_file = None,  # filepath to the ssl *.pem file for https
            **kwargs):             # currently unused

        # by default Syncthing UI will run on an https interface,
        # but there is no supplied ssl key. This will throw a warning
        # but not prevent execution; just a console alert.
        if is_https and ssl_cert_file is None:
            warnings.warn('Using HTTPS without specified ssl_cert_file.')

        self.api_key = api_key
        self.host = host
        self.port = port
        self.protocol = 'https' if is_https else 'http'

        # the lowest the timeout can be is 0.5 seconds
        self.timeout = max(MIN_TIMEOUT_SECS, timeout)

        self.cert = ssl_cert_file
        self.verify = True if self.cert else False

        # all POST requests to the API need the X-API-Key header
        self.req_headers = {
            'X-API-Key': self.api_key
        }

        # cached "is_connected"
        self.last_request = None

    @property
    def root(self):
        return '%s://%s:%d' % (self.protocol, self.host, self.port)

    @property
    def is_connected(self):
        if not self.last_request:
            self.req('/', 'GET')
        return self.last_request

    @staticmethod
    def from_dict(d):
        """Returns an Interface from a dictionary config"""
        return Interface(**d)

    @staticmethod
    def from_json(json_str):
        """Returns an Interface from a JSON string"""
        return Interface.from_dict(json.dumps(json_str))

    def to_json(self):
        """Exports Interface configuration as JSON"""
        return json.dumps({
            'api_key': self.api_key,
            'host': self.host,
            'port': self.port,
            'timeout': self.timeout,
            'is_https': self.protocol == 'https',
            'ssl_cert_file': self.cert})

    def req(self, endpoint, verb, **kwargs):
        # http verb, GET/POST/DELETE etc
        verb = verb.upper()
        if verb not in VERB_SWAPS.keys():
            raise UserWarning('Unsupported HTTP verb in REST request.')
        the_url = uparse.urljoin(self.root, endpoint)

        try:
            with warnings.catch_warnings():
                # supress exceptions for an insecure request if we don't have
                # a cert file defined in the constructor.
                if not self.cert:
                    warnings.simplefilter('ignore', exceptions.InsecureRequestWarning)

                resp = requests.request(
                    verb,
                    the_url,
                    params = kwargs,
                    timeout = self.timeout,
                    verify = self.verify,
                    cert = self.cert,
                    headers = self.req_headers)
        except requests.RequestException as e:
            self.last_request = False
            raise
        else:
            self.last_request = resp.status_code == 200
            if 'json' in resp.headers.get('content-type', 'text/plain').lower():
                return Bunch(resp.json())
            else:
                return resp
