#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     Copyright (c) 2016, Blake VandeMerwe
#
#       Permission is hereby granted, free of charge, to any person obtaining
#       a copy of this software and associated documentation files
#       (the "Software"), to deal in the Software without restriction,
#       including without limitation the rights to use, copy, modify, merge,
#       publish, distribute, sublicense, and/or sell copies of the Software,
#       and to permit persons to whom the Software is furnished to do so, subject
#       to the following conditions: The above copyright notice and this permission
#       notice shall be included in all copies or substantial portions
#       of the Software.
#
#     python-syncthing, 2016
# <<
from __future__ import unicode_literals

import os
import json
import logging

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10.0

__all__ = ['SyncthingError', 'BaseAPI', 'System',
           'Database', 'Statistics', 'Syncthing']


class SyncthingError(Exception):
    pass


class BaseAPI(object):
    prefix = ''

    def __init__(self, api_key, host='localhost', port=8384, timeout=DEFAULT_TIMEOUT,
                    is_https=False, ssl_cert_file=None):

        if is_https and not ssl_cert_file:
            logger.warning('using https without specifying ssl_cert_file')

        if ssl_cert_file:
            if not os.path.exists(ssl_cert_file):
                raise SyncthingError('ssl_cert_file does not exist at location, %s' % ssl_cert_file)

        self.api_key = api_key
        self.host = host
        self.is_https = is_https
        self.port = port
        self.ssl_cert_file = ssl_cert_file
        self.timeout = timeout
        self.verify = True if ssl_cert_file else False
        self._headers = {
            'X-API-Key': api_key
        }
        self.url = '{proto}://{host}:{port}'.format(
            proto='https' if is_https else 'http', host=host, port=port)
        self._base_url = self.url + '{endpoint}'

    def get(self, endpoint, data=None, headers=None, params=None):
        endpoint = self.prefix + endpoint
        return self._request('GET', endpoint, data, headers, params)

    def post(self, endpoint, data=None, headers=None, params=None):
        endpoint = self.prefix + endpoint
        return self._request('POST', endpoint, data, headers, params)

    def _request(self, method, endpoint, data=None, headers=None, params=None):
        method = method.upper()

        endpoint = self._base_url.format(endpoint=endpoint)

        if method not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise SyncthingError('unsupported http verb requested, %s' % method)

        if data is None:
            data = {}
        assert isinstance(data, dict)

        if headers is None:
            headers = {}
        assert isinstance(headers, dict)

        headers.update(self._headers)

        try:
            resp = requests.request(
                method,
                endpoint,
                data=json.dumps(data),
                params=params,
                timeout=self.timeout,
                verify=self.verify,
                cert=self.ssl_cert_file,
                headers=headers
            )
            resp.raise_for_status()

        except requests.RequestException as e:
            logger.exception(e)
            raise SyncthingError(e)

        else:
            if resp.status_code != requests.codes.ok:
                logger.error('%d %s (%s): %s', resp.status_code, resp.reason,
                                resp.url, resp.text)
                return resp

            if 'json' in resp.headers.get('Content-Type', 'text/plain').lower():
                j =  resp.json()

            else:
                content = resp.content.decode('utf-8')
                if content[0] == '{' and content[-1] == '}':
                    j = json.loads(content)

                else:
                    return content

            if isinstance(j, dict) and j.get('error'):
                api_err = j.get('error')
                raise SyncthingError(api_err)

            return j


class System(BaseAPI):
    prefix = '/rest/system/'


class Database(BaseAPI):
    prefix = '/rest/db/'


class Statistics(BaseAPI):
    prefix = '/rest/stats/'

    def device(self):
        return self.get('device')

    def folder(self):
        return self.get('folder')


class Misc(BaseAPI):
    prefix = '/rest/svc/'

    def device_id(self, id_):
        """ Verifies and formats a device ID. Accepts all currently valid formats
            (52 or 56 characters with or without separators, upper or lower case,
            with trivial substitutions). Takes one parameter, id, and returns
            either a valid device ID in modern format, or an error.

            Args:
                id_ (str)

            Raises:
                SyncthingError: when ``id_`` is an invalid length.

            Returns:
                str
        """
        return self.get('deviceid', params={'id': id_}).get('id')

    def language(self):
        """ Returns a list of canonicalized localization codes, as picked up from
            the Accept-Language header sent by the browser. By default, this API
            will return a single element that's empty; however calling
            :func:`Misc.get` directly with `lang` you can set specific headers
            to get values back as intended.

            Returns:
                List[str]
        """
        return self.get('lang')

    def random_string(self, length=32):
        """ Returns a strong random generated string (alphanumeric) of the
            specified length.

            Args:
                length (int): default ``32``.

            Returns:
                str
        """
        return self.get('random/string', params={'length': length}).get('random', None)

    def report(self):
        """ Returns the data sent in the anonymous usage report.

            Returns:
                dict
        """
        return self.get('report')


class Syncthing(object):
    def __init__(self, api_key, host='localhost', port=8384, timeout=DEFAULT_TIMEOUT,
                    is_https=False, ssl_cert_file=None):

        self.api_key = api_key
        self.host = host
        self.port = port
        self.timeout = timeout
        self.is_https = is_https
        self.ssl_cert_file = ssl_cert_file

        kwargs = {
            'host': host, 'port': port, 'timeout': timeout, 'is_https': is_https,
                'ssl_cert_file': ssl_cert_file
        }

        self.system = System(api_key, **kwargs)
        self.database = Database(api_key, **kwargs)
        self.stats = Statistics(api_key, **kwargs)
        self.misc = Misc(api_key, **kwargs)