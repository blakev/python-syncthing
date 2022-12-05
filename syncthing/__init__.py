#! /usr/bin/env python
# -*- coding: utf-8 -*-
# >>
#     Copyright (c) 2016-2017, Blake VandeMerwe
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
import sys
import json
import logging
import warnings
from collections import namedtuple
import collections.abc

import requests
from dateutil.parser import parse as dateutil_parser
from requests.exceptions import Timeout
from urllib3.exceptions import TimeoutError

PY2 = sys.version_info[0] < 3

if PY2:
    string_types = (basestring, str, unicode,)
    def reraise(msg, base):
        raise Syncthing(msg)

else:
    string_types = (str,)
    def reraise(msg, exc):
        raise SyncthingError(msg) from exc

logger = logging.getLogger(__name__)


NoneType = type(None)
DEFAULT_TIMEOUT = 10.0

__all__ = ['SyncthingError', 'ErrorEvent', 'BaseAPI', 'System',
           'Config', 'Cluster', 'Folder', 'Database', 'Statistics', 'Syncthing',
           # methods
           'keys_to_datetime', 'parse_datetime']

ErrorEvent = namedtuple('ErrorEvent', 'when, message')
"""tuple[datetime.datetime,str]: used to process error lists more easily, 
instead of by two-key dictionaries. """

def _syncthing():
    KEY = os.getenv('SYNCTHING_API_KEY')
    HOST = os.getenv('SYNCTHING_HOST', '127.0.0.1')
    PORT = os.getenv('SYNCTHING_PORT', 8384)
    IS_HTTPS = bool(int(os.getenv('SYNCTHING_HTTPS', '0')))
    SSL_CERT_FILE = os.getenv('SYNCTHING_CERT_FILE')
    return Syncthing(KEY, HOST, PORT, 10.0, IS_HTTPS, SSL_CERT_FILE)


def keys_to_datetime(obj, *keys):
    """ Converts all the keys in an object to DateTime instances.

        Args:
            obj (dict): the JSON-like ``dict`` object to modify inplace.
            keys (str): keys of the object being converted into DateTime
                instances.

        Returns:
            dict: ``obj`` inplace.

        >>> keys_to_datetime(None) is None
        True
        >>> keys_to_datetime({})
        {}
        >>> a = {}
        >>> id(keys_to_datetime(a)) == id(a)
        True
        >>> a = {'one': '2016-06-06T19:41:43.039284',
                 'two': '2016-06-06T19:41:43.039284'}
        >>> keys_to_datetime(a) == a
        True
        >>> keys_to_datetime(a, 'one')['one']
        datetime.datetime(2016, 6, 6, 19, 41, 43, 39284)
        >>> keys_to_datetime(a, 'one')['two']
        '2016-06-06T19:41:43.039284'
    """
    if not keys:
        return obj
    for k in keys:
        if k not in obj:
            continue
        v = obj[k]
        if not isinstance(v, string_types):
            continue
        obj[k] = parse_datetime(v)
    return obj


def parse_datetime(s, **kwargs):
    """ Converts a time-string into a valid
    :py:class:`~datetime.datetime.DateTime` object.

        Args:
            s (str): string to be formatted.

        ``**kwargs`` is passed directly to :func:`.dateutil_parser`.

        Returns:
            :py:class:`~datetime.datetime.DateTime`
    """
    if not s:
        return None
    try:
        ret = dateutil_parser(s, **kwargs)
    except (OverflowError, TypeError, ValueError) as e:
        reraise('datetime parsing error from %s' % s, e)
    return ret


class SyncthingError(Exception):
    """Base Syncthing Exception class all non-assert errors will raise from."""


class BaseAPI(object):
    """ Placeholder for HTTP REST API URL prefix. """

    prefix = ''

    def __init__(self, api_key, host='localhost', port=8384,
                 timeout=DEFAULT_TIMEOUT, is_https=False, ssl_cert_file=None):

        if ssl_cert_file:
            if not os.path.exists(ssl_cert_file):
                raise SyncthingError(
                    'ssl_cert_file does not exist at location, %s' %
                    ssl_cert_file)

        self.api_key = api_key
        self.host = host
        self.is_https = is_https
        self.port = port
        self.ssl_cert_file = ssl_cert_file
        self.timeout = timeout
        self.verify = True if ssl_cert_file or is_https else False
        self._headers = {
            'X-API-Key': api_key
        }
        self.url = '{proto}://{host}:{port}'.format(
            proto='https' if is_https else 'http', host=host, port=port)
        self._base_url = self.url + '{endpoint}'

    def get(self, endpoint, data=None, headers=None, params=None,
            return_response=False, raw_exceptions=False, stream=False):
        endpoint = self.prefix + endpoint
        return self._request('GET', endpoint, data, headers, params,
                             return_response, raw_exceptions, stream)

    def post(self, endpoint, data=None, headers=None, params=None,
             return_response=False, raw_exceptions=False):
        endpoint = self.prefix + endpoint
        return self._request('POST', endpoint, data, headers, params,
                             return_response, raw_exceptions)

    def put(self, endpoint, data=None, headers=None, params=None,
             return_response=False, raw_exceptions=False):
        endpoint = self.prefix + endpoint
        return self._request('PUT', endpoint, data, headers, params,
                             return_response, raw_exceptions)

    def patch(self, endpoint, data=None, headers=None, params=None,
             return_response=False, raw_exceptions=False):
        endpoint = self.prefix + endpoint
        return self._request('PATCH', endpoint, data, headers, params,
                             return_response, raw_exceptions)

    def delete(self, endpoint, data=None, headers=None, params=None,
             return_response=False, raw_exceptions=False):
        endpoint = self.prefix + endpoint
        return self._request('DELETE', endpoint, data, headers, params,
                             return_response, raw_exceptions)

    def _request(self, method, endpoint, data=None, headers=None, params=None,
                    return_response=False, raw_exceptions=False, stream=False):
        method = method.upper()

        endpoint = self._base_url.format(endpoint=endpoint)

        if method not in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
            raise SyncthingError(
                'unsupported http verb requested, %s' % method)

        if data is None:
            data = {}
        assert isinstance(data, string_types) or isinstance(data, dict) or isinstance (data, collections.abc.Sequence)

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
                cert=self.ssl_cert_file,
                headers=headers,
                stream=stream
            )

            if not return_response:
                resp.raise_for_status()

        except requests.RequestException as e:
            if raw_exceptions:
                raise e
            reraise('http request error', e)

        else:
            if return_response:
                return resp

            if resp.status_code != requests.codes.ok:
                logger.error('%d %s (%s): %s', resp.status_code, resp.reason,
                                resp.url, resp.text)
                return resp

            if 'json' in resp.headers.get('Content-Type', 'text/plain')\
                    .lower():
                json_data = resp.json()

            if resp.headers.get('Content-Type', 'application/zip').lower():
                return resp

            else:
                content = resp.content.decode('utf-8')
                if content and content[0] == '{' and content[-1] == '}':
                    json_data = json.loads(content)

                else:
                    return content

            if isinstance(json_data, dict) and json_data.get('error'):
                api_err = json_data.get('error')
                raise SyncthingError(api_err)
            return json_data

class System(BaseAPI):
    """ HTTP REST endpoint for System calls."""

    prefix = '/rest/system/'

    def browse(self, path=None):
        """ Returns a list of directories matching the path given.

        Args:
            path (str): glob pattern.

        Returns:
            List[str]
        """
        params = None
        if path:
            assert isinstance(path, string_types)
            params = {'current': path}
        return self.get('browse', params=params)

    def config(self):
        """ DEPRECATED. Use :class:`Config` instead.

            Returns the current configuration.

            Returns:
                dict

            >>> s = _syncthing().system
            >>> config = s.config()
            >>> config
            ... # doctest: +ELLIPSIS
            {...}
            >>> 'version' in config and config['version'] >= 15
            True
            >>> 'folders' in config
            True
            >>> 'devices' in config
            True
        """
        return self.get('config')

    def set_config(self, config, and_restart=False):
        """ DEPRECATED. Use :class:`Config` instead.

            Use Post the full contents of the configuration, in the same format as
            returned by :func:`.config`. The configuration will be saved to disk
            and the ``configInSync`` flag set to ``False``. Restart Syncthing to
            activate.
        """
        assert isinstance(config, dict)
        self.post('config', data=config)
        if and_restart:
            self.restart()

    def config_insync(self):
        """ DEPRECATED. Use :func:`restart_required` instead.

            Returns whether the config is in sync, i.e. whether the running
            configuration is the same as that on disk.

            Returns:
                bool
        """
        status = self.get('config/insync').get('configInSync', False)
        if status is None:
            status = False
        return status

    def connections(self):
        """ Returns the list of configured devices and some metadata
            associated with them. The list also contains the local device
            itself as not connected.

            Returns:
                dict

            >>> s = _syncthing().system
            >>> connections = s.connections()
            >>> sorted([k for k in connections.keys()])
            ['connections', 'total']
            >>> isinstance(connections['connections'], dict)
            True
            >>> isinstance(connections['total'], dict)
            True
        """
        return self.get('connections')

    def debug(self):
        """ Returns the set of debug facilities and which of them are
            currently enabled.

            Returns:
                dict

            >>> s = _syncthing().system
            >>> debug = s.debug()
            >>> debug
            ... #doctest: +ELLIPSIS
            {...}
            >>> len(debug.keys())
            2
            >>> 'enabled' in debug and 'facilities' in debug
            True
            >>> isinstance(debug['enabled'], list) or debug['enabled'] is None
            True
            >>> isinstance(debug['facilities'], dict)
            True
        """
        return self.get('debug')

    def disable_debug(self, *on):
        """ Disables debugging for specified facilities.

            Args:
                on (str): debugging points to apply ``disable``.

            Returns:
                None
        """
        self.post('debug', params={'disable': ','.join(on)})

    def enable_debug(self, *on):
        """ Enables debugging for specified facilities.

            Args:
                on (str): debugging points to apply ``enable``.

            Returns:
                None
        """
        self.post('debug', params={'enable': ','.join(on)})

    def discovery(self):
        """ Returns the contents of the local discovery cache.

            Returns:
                dict
        """
        return self.get('discovery')

    def add_discovery(self, device, address):
        """ Add an entry to the discovery cache.

            Args:
                device (str): Device ID.
                address (str): destination address, a valid hostname or
                    IP address that's serving a Syncthing instance.

            Returns:
                None
        """
        self.post('discovery', params={'device': device,
                                       'address': address})

    def clear(self):
        """ Remove all recent errors.

            Returns:
                None
        """
        self.post('error/clear')


    def clear_errors(self):
        """ Alias function for :meth:`.clear`. """
        self.clear()

    def errors(self):
        """ Returns the list of recent errors.

            Returns:
                list: of :obj:`.ErrorEvent` tuples.
        """
        ret_errs = list()
        errors = self.get('error').get('errors', None) or list()
        assert isinstance(errors, list)
        for err in errors:
            when = parse_datetime(err.get('when', None))
            msg = err.get('message', '')
            e = ErrorEvent(when, msg)
            ret_errs.append(e)
        return ret_errs

    def show_error(self, message):
        """ Send an error message to the active client. The new error will be
            displayed on any active GUI clients.

            Args:
                message (str): Plain-text message to display.

            Returns:
                None

            >>> s = _syncthing()
            >>> s.system.show_error('my error msg')
            >>> s.system.errors()[0]
            ... # doctest: +ELLIPSIS
            ErrorEvent(when=datetime.datetime(...), message='"my error msg"')
            >>> s.system.clear_errors()
            >>> s.system.errors()
            []
        """
        assert isinstance(message, string_types)
        self.post('error', data=message)

    def log(self):
        """ Returns the list of recent log entries.

            Returns:
                dict
        """
        return self.get('log')

    def paths(self):
        """ Returns the path locations used internally for storing configuration, database, and others. 

            Returns:
                dict
        """
        return self.get('paths')

    def pause(self, device):
        """ Pause the given device.

            Args:
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        resp = self.post('pause', params={'device': device},
                         return_response=True)
        error = resp.text
        if not error:
            error = None
        return {'success': resp.status_code == requests.codes.ok,
                'error': error}

    def ping(self, with_method='GET'):
        """ Pings the Syncthing server.

            Args:
                with_method (str): uses a given HTTP method, options are
                    ``GET`` and ``POST``.

            Returns:
                dict
        """
        assert with_method in ('GET', 'POST')
        if with_method == 'GET':
            return self.get('ping')
        return self.post('ping')

    def reset(self):
        """ Erase the current index database and restart Syncthing.

            Returns:
                None
        """
        warnings.warn('This is a destructive action that cannot be undone.')
        self.post('reset', data={})

    def reset_folder(self, folder):
        """ Erase the database index from a given folder and restart Syncthing.

            Args:
                folder (str): Folder ID.

            Returns:
                None
        """
        warnings.warn('This is a destructive action that cannot be undone.')
        self.post('reset', data={}, params={'folder': folder})

    def restart(self):
        """ Immediately restart Syncthing.

            Returns:
                None
        """
        self.post('restart', data={})

    def resume(self, device):
        """ Resume the given device.

            Args:
                device (str): Device ID.

            Returns:
                dict: with keys ``success`` and ``error``.
        """
        resp = self.post('resume', params={'device': device},
                         return_response=True)
        error = resp.text
        if not error:
            error = None
        return {'success': resp.status_code == requests.codes.ok,
                'error': error}

    def shutdown(self):
        """ Causes Syncthing to exit and not restart.

            Returns:
                None
        """
        self.post('shutdown', data={})

    def status(self):
        """ Returns information about current system status and resource usage.

            Returns:
                dict
        """
        resp = self.get('status')
        resp = keys_to_datetime(resp, 'startTime')
        return resp

    def upgrade(self):
        """ Checks for a possible upgrade and returns an object describing
            the newest version and upgrade possibility.

            Returns:
                dict
        """
        return self.get('upgrade')

    def can_upgrade(self):
        """ Returns when there's a newer version than the instance running.

            Returns:
                bool
        """
        return (self.upgrade() or {}).get('newer', False)

    def do_upgrade(self):
        """ Perform an upgrade to the newest released version and restart.
            Does nothing if there is no newer version than currently running.

            Returns:
                None
        """
        return self.post('upgrade')

    def version(self):
        """ Returns the current Syncthing version information.

            Returns:
                dict
        """
        return self.get('version')

class Config(BaseAPI):
    """ HTTP REST endpoint for Config calls."""

    prefix = '/rest/config/'

    def config(self):
        """ Returns the full config.
            
            Returns:
                dict
        """

        return self.get('')

    def put_config(self, config):
        """ Replaces the entire object.

            Args:
                config (dict): Complete configuration file
        """

        return self.put('', data=config)

    def restart_required(self):
        """ Returns whether a restart of Syncthing is required for the current config to take effect.

            Returns:
                dict
        """

        return self.get('restart-required')

    def folders(self, id=None):
        """ Returns all folders. Optionally supply an ID to return a single folder.

            Args:
                id (str, optional): ID of the folder to return
            
            Returns:
                dict
        """

        if(id):
            return self.get('folders/' + id)
        else:
            return self.get('folders')

    def put_folders(self, config, id=None):
        """ Replaces the entire object. Optionally supply an ID to replace the entire config for a single folder.

            Args:
                config (dict): Complete config
                id (str, optional): ID 
        """

        if(id):
            return self.put('folders/' + id, data=config)
        else:
            return self.put('folders', data=config)
    
    def post_folders(self, config):
        """ Add a single folder.

            Args:
                config (dict): Config of the folder to add
        """

        return self.post('folders', data=config)

    def patch_folders(self, config, id):
        """ Replaces only the given child objects.

            Args:
                config (dict): Selective config
                id (str): ID of the folder to patch
        """

        return self.patch('folders/' + id, data=config)
    
    def delete_folders(self, id):
        """ Delete a single folder matching the given ID.

            Args:
                id (str): ID of the folder to delete
        """

        return self.delete('folders/' + id)

    def devices(self, id=None):
        """ Returns all devices. Optionally specificy an ID to return a single device.

            Args:
                id (str): ID of the device to return

            Returns:
                dict
        """

        if(id):
            return self.get('devices/' + id)
        else:
            return self.get('devices')

    def put_devices(self, config, id=None):
        """ Replaces the entire devices object. Optionally specify an ID to replace the config of a single device.

            Args:
                config (dict): Entire config
                id (str, optional): ID of the device
        """

        if(id):
            return self.put('devices/' + id, data=config)
        else:
            return self.put('devices', data=config)

    def post_devices(self, config):
        """ Add a single devices.

            Args:
                config (dict): Config of the device to add
        """

        return self.post('devices', data=config)

    def patch_devices(self, config, id):
        """ Replaces only the given child objects.

            Args:
                config (dict): Selective config
                id (str): ID of the device
        """

        return self.patch('devices/' + id, data=config)
    
    def delete_devices(self, id):
        """ Delete a device with a given ID.

            Args:
                id (str): ID of the device
        """

        return self.delete('devices/' + id)
    
    def defaults_folder(self):
        """ Get default folder object.

            Returns:
                dict
        """
        return self.get('defaults/folder')

    def put_defaults_folder(self, config):
        """ Replaces the entire defaults folder object.

            Args:
                config (dict): Entire config
        """
        return self.put('defaults/folder', data=config)

    def patch_defaults_folder(self, config):
        """ Replaces only the given child objects.

            Args:
                config (dict): Selective config
        """
        return self.patch('defaults/folder', data=config)

    def defaults_device(self):
        """ Get default device object.

            Returns:
                dict
        """
        return self.get('defaults/device')

    def put_defaults_device(self, config):
        """ Replaces the entire object.

            Args:
                config (dict): Entire config
        """
        return self.put('defaults/device', data=config)

    def patch_defaults_device(self, config):
        """ Replaces only the given child objects.

            Args:
                config (dict): Selective config
        """
        return self.patch('defaults/device', data=config)
    
    def defaults_ignores(self):
        """ Get default ignores object.

            Returns:
                dict
        """
        return self.get('defaults/ignores')
    
    def put_defaults_ignores(self, config):
        """ Replaces the entire object.

            Args:
                config (dict): Entire config
        """
        return self.put('defaults/ignores', data=config)

    def options(self):
        """ Get default options object.
        
            Returns:
                dict
        """
        return self.get('options')
    
    def put_options(self, config):
        """ Replaces the entire object.
            
            Args:
                config (dict): Entire config
        """
        return self.put('options', data=config)
    
    def patch_options(self, config):
        """ Replaces only the given child objects.

            Args:
                config (dict): Selective config
        """
        return self.patch('options', data=config)
    
    def ldap(self):
        """ Returns the LDAP object.
            
            Returns:
                dict
        """
        return self.get('ldap')
    
    def put_ldap(self, config):
        """ Replaces the entire object.

            Args:
                config (dict): Entire config
        """
        return self.put('ldap', data=config)
    
    def patch_ldap(self, config):
        """ Replaces only the given child objects.

            Args:
                config (dict): Selective config
        """
        return self.patch('ldap', data=config)

    def gui(self):
        """ Returns the GUI object

            Returns:
                dict
        """
        return self.get('gui')
    
    def put_gui(self, config):
        """ Replaces the entire object.

            Args:
                config (dict): Entire config
        """
        return self.put('gui', data=config)
    
    def patch_gui(self, config):
        """ Replaces only the given child objects 

            Args:
                config (dict): Selective config

            >>> s = _syncthing().config
            >>> s.patch_gui({'address': '0.0.0.0:8384'})
            ''
            >>> gui = s.gui()
            >>> '0.0.0.0' in gui['address']
            True
        """
        return self.patch('gui', data=config)

class Cluster(BaseAPI):
    """ HTTP REST endpoint for Cluster calls."""

    prefix = '/rest/cluster/pending/'

    def devices (self):
        """ Lists remote devices which have tried to connect, but are not yet 
            configured in the instance.

            Returns:
                dict
        """
        return self.get('devices') 

    def delete_devices(self, device):
        """ Remove records about a pending remote device which tried to connect. 

            Args:
                device (str): ID of the device to delete
        """
        return self.delete('devices', params={'device': device})

    def folders (self, device=None):
        """ Lists folders which remote devices have offered to us, but are not yet 
            shared from our instance to them.

            Optionally supply a device ID to only return folders offered by a specific 
            remote device

            Args:
                device (str, optional): 

            Returns: 
                dict
        """
        if (device):
            return self.get('devices', params={'device': device}) 
        else:
            return self.get('devices') 
        
    def delete_folders(self, folder, device=None):
        """ Remove records about a pending folder announced from a remote device.

            Optionally specify a device ID to only affect announcements of the given 
            folder from the given device, or from any device if omitted.

            Args:
                folder (str): ID of the folder to delete
                device (str, optional): ID of the device
        """
        if (device):
            return self.delete('folders', params={'folder': folder, 'device': device})
        else:
            return self.delete('folders', params={'folder': folder})

class Folder(BaseAPI):
    """ HTTP REST endpoint for Folder calls."""

    prefix = '/rest/folder/'

    def errors(self, folder, page=None, perpage=None):
        """ Returns the list of errors encountered during scanning or pulling.

            Args:
                folder (str): ID of the folder
                page (str, optional): advances in the results by that given number of pages
                perpage (str, optional): number of entries to return per page
        """

        return self.get('errors', params={'folder': folder, 'page': page, 'perpage': perpage})

    def versions(self, folder):
        """ Returns the list of archived files that could be recovered.

            Args:
                folder (str): ID of the folder

            Returns:
                dict
        """
        return self.get('versions', params={'folder': folder})
    
    def post_versions(self, folder, data):
        """ Restore archived versions of a given set of files.  Expects an object with 
            attributes named after the relative file paths, with timestamps as values 
            matching valid versionTime entries in the corresponding :func:`versions` response object.

            Args:
                data (dict): Object with attributes named after the relative file paths
                folder (str): ID of the folder

            Returns:
                dict: Contains any error messages that occured during the restoration 
                    of the file, with the file path as attribute name.
        """
        return self.post('versions', params={'folder': folder}, data=data)

class Database(BaseAPI):
    """ HTTP REST endpoint for Database calls."""

    prefix = '/rest/db/'

    def browse(self, folder, levels=None, prefix=None):
        """ Returns the directory tree of the global model.

            Directories are always JSON objects (map/dictionary), and files are
            always arrays of modification time and size. The first integer is
            the files modification time, and the second integer is the file
            size.

            Args:
                folder (str): The root folder to traverse.
                levels (int): How deep within the tree we want to dwell down.
                    (0 based, defaults to unlimited depth)
                prefix (str): Defines a prefix within the tree where to start
                    building the structure.

            Returns:
                dict
        """
        assert isinstance(levels, int) or levels is None
        assert isinstance(prefix, string_types) or prefix is None
        return self.get('browse', params={'folder': folder,
                                          'levels': levels,
                                          'prefix': prefix})

    def completion(self, device, folder):
        """ Returns the completion percentage (0 to 100) for a given device
            and folder.

            Args:
                device (str): The Syncthing device the folder is syncing to.
                folder (str): The folder that is being synced.

            Returns:
                int
        """
        return self.get(
            'completion',
            params={'folder': folder, 'device': device}
        ).get('completion', None)

    def file(self, folder, file_):
        """ Returns most data available about a given file, including version
            and availability.

            Args:
                folder (str):
                file_ (str):

            Returns:
                dict
        """
        return self.get('file', params={'folder': folder,
                                        'file': file_})

    def ignores(self, folder):
        """ Returns the content of the ``.stignore`` as the ignore field. A
        second field, expanded, provides a list of strings which represent
        globbing patterns described by gobwas/glob (based on standard
        wildcards) that match the patterns in ``.stignore`` and all the
        includes.

        If appropriate these globs are prepended by the following modifiers:
        ``!`` to negate the glob, ``(?i)`` to do case insensitive matching and
        ``(?d)`` to enable removing of ignored files in an otherwise empty
        directory.

            Args:
                folder

            Returns:
                dict
        """
        return self.get('ignores', params={'folder': folder})

    def set_ignores(self, folder, *patterns):
        """ Applies ``patterns`` to ``folder``'s ``.stignore`` file.

            Args:
                folder (str):
                patterns (str):

            Returns:
                dict
        """
        if not patterns:
            return {}
        data = {'ignore': list(patterns)}
        return self.post('ignores', params={'folder': folder}, data=data)

    def need(self, folder, page=None, perpage=None):
        """ Returns lists of files which are needed by this device in order
        for it to become in sync.

            Args:
                folder (str):
                page (int): If defined applies pagination accross the
                    collection of results.
                perpage (int): If defined applies pagination across the
                    collection of results.

            Returns:
                dict
        """
        assert isinstance(page, int) or page is None
        assert isinstance(perpage, int) or perpage is None
        return self.get('need', params={'folder': folder,
                                 'page': page,
                                 'perpage': perpage})

    def override(self, folder):
        """ Request override of a send-only folder.

            Args:
                folder (str): folder ID.

            Returns:
                dict
        """
        self.post('override', params={'folder': folder})

    def prio(self, folder, file_):
        """ Moves the file to the top of the download queue.

            Args:
                folder (str):
                file_ (str):

            Returns:
                dict
        """
        self.post('prio', params={'folder': folder,
                                  'file': file_})

    def scan(self, folder, sub=None, next_=None):
        """ Request immediate rescan of a folder, or a specific path within a
        folder.

            Args:
                folder (str): Folder ID.
                sub (str): Path relative to the folder root. If sub is omitted
                    the entire folder is scanned for changes, otherwise only
                    the given path children are scanned.
                next_ (int): Delays Syncthing's automated rescan interval for
                    a given amount of seconds.

            Returns:
                str
        """
        if not sub:
            sub = ''
        assert isinstance(sub, string_types)
        assert isinstance(next_, int) or next_ is None
        return self.post('scan', params={'folder': folder,
                                         'sub': sub,
                                         'next': next_})

    def status(self, folder):
        """ Returns information about the current status of a folder.

            Note:
                This is an expensive call, increasing CPU and RAM usage on the
                device. Use sparingly.

            Args:
                folder (str): Folder ID.

            Returns:
                dict
        """
        return self.get('status', params={'folder': folder})


class Events(BaseAPI):
    """ HTTP REST endpoints for Event based calls.

        Syncthing provides a simple long polling interface for exposing events
        from the core utility towards a GUI.

        .. code-block:: python

           syncthing = Syncthing()
           event_stream = syncthing.events(limit=5)

           for event in event_stream:
               print(event)
               if event_stream.count > 10:
                   event_stream.stop()
    """

    prefix = '/rest/'

    def __init__(self, api_key, last_seen_id=None, filters=None, limit=None,
                 *args, **kwargs):
        if 'timeout' not in kwargs:
            # increase our timeout to account for long polling.
            # this will reduce the number of timed-out connections, which are
            # swallowed by the library anyway
            kwargs['timeout'] = 60.0  #seconds

        super(Events, self).__init__(api_key, *args, **kwargs)
        self._last_seen_id = last_seen_id or 0
        self._filters = filters
        self._limit = limit

        self._count = 0
        self.blocking = True

    @property
    def count(self):
        """ The number of events that have been processed by this event stream.

            Returns:
                int
        """
        return self._count

    @property
    def last_seen_id(self):
        """ The id of the last seen event.

            Returns:
                int
        """
        return self._last_seen_id

    def disk_events(self):
        """ Blocking generator of disk related events. Each event is
        represented as a ``dict`` with metadata.

            Returns:
                generator[dict]
        """
        for event in self._events('events/disk', None, self._limit):
            yield event

    def stop(self):
        """ Breaks the while-loop while the generator is polling for event
            changes.

            Returns:
                  None
        """
        self.blocking = False

    def _events(self, using_url, filters=None, limit=None):
        """ A long-polling method that queries Syncthing for events..

            Args:
                using_url (str): REST HTTP endpoint
                filters (List[str]): Creates an "event group" in Syncthing to
                    only receive events that have been subscribed to.
                limit (int): The number of events to query in the history
                    to catch up to the current state.

            Returns:
                generator[dict]
        """

        # coerce
        if not isinstance(limit, (int, NoneType)):
            limit = None

        # coerce
        if filters is None:
            filters = []

        # format our list into the correct expectation of string with commas
        if isinstance(filters, string_types):
            filters = filters.split(',')

        # reset the state if the loop was broken with `stop`
        if not self.blocking:
            self.blocking = True

        # block/long-poll for updates to the events api
        while self.blocking:
            params = {
                'since': self._last_seen_id,
                'limit': limit,
            }

            if filters:
                params['events'] = ','.join(map(str, filters))

            try:
                data = self.get(using_url, params=params, raw_exceptions=True)
            except (Timeout, TimeoutError) as e:
                # swallow timeout errors for long polling
                data = None
            except Exception as e:
                reraise('', e)

            if data:
                for event in data:
                    # handle potentially multiple events returned in a list
                    self._count += 1
                    yield event
                # update our last_seen_id to move our event counter forward
                self._last_seen_id = data[-1]['id']

    def __iter__(self):
        """ Helper interface for :obj:`._events` """
        for event in self._events('events', self._filters, self._limit):
            yield event


class Statistics(BaseAPI):
    """ HTTP REST endpoint for Statistic calls."""

    prefix = '/rest/stats/'

    def device(self):
        """ Returns general statistics about devices.

            Currently, only contains the time the device was last seen.

            Returns:
                dict
        """
        return self.get('device')

    def folder(self):
        """ Returns general statistics about folders.

            Currently contains the last scan time and the last synced file.

            Returns:
                dict
        """
        return self.get('folder')


class Misc(BaseAPI):
    """ HTTP REST endpoint for Miscelaneous calls."""

    prefix = '/rest/svc/'

    def device_id(self, id_):
        """ Verifies and formats a device ID. Accepts all currently valid
        formats (52 or 56 characters with or without separators, upper or lower
        case, with trivial substitutions). Takes one parameter, id, and returns
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
        """ Returns a list of canonicalized localization codes, as picked up
        from the Accept-Language header sent by the browser. By default, this
        API will return a single element that's empty; however calling
        :func:`Misc.get` directly with `lang` you can set specific headers to
        get values back as intended.

        Returns:
            List[str]

            >>> s = _syncthing()
            >>> len(s.misc.language())
            1
            >>> s.misc.language()[0]
            ''
            >>> s.misc.get('lang', headers={'Accept-Language': 'en-us'})
            ['en-us']
        """
        return self.get('lang')

    def random_string(self, length=32):
        """ Returns a strong random generated string (alphanumeric) of the
            specified length.

            Args:
                length (int): default ``32``.

            Returns:
                str

            >>> s = _syncthing()
            >>> len(s.misc.random_string())
            32
            >>> len(s.misc.random_string(32))
            32
            >>> len(s.misc.random_string(1))
            1
            >>> len(s.misc.random_string(0))
            32
            >>> len(s.misc.random_string(None))
            32
            >>> import string
            >>> all_letters = string.ascii_letters + string.digits
            >>> all([c in all_letters for c in s.misc.random_string(128)])
            True
            >>> all([c in all_letters for c in s.misc.random_string(1024)])
            True
        """
        return self.get(
            'random/string',
            params={'length': length}
        ).get('random', None)

    def report(self):
        """ Returns the data sent in the anonymous usage report.

            Returns:
                dict

            >>> s = _syncthing()
            >>> report = s.misc.report()
            >>> 'version' in report
            True
            >>> 'longVersion' in report
            True
            >>> 'syncthing v' in report['longVersion']
            True
        """
        return self.get('report')

class Debug(BaseAPI):
    """ HTTP REST endpoint for Debug calls.

        These endpoints require the gui.debugging configuration option to 
        be enabled and yields an access denied error code otherwise.
    """

    prefix = '/rest/debug/'

    def peerCompletion(self):
        """ Summarizes the completion precentage for each remote device. 

            Returns:
                dict
        """
        return self.get('peerCompletion')

    def httpmetrics(self):
        """ Returns statistics about each served REST API endpoint.

            Returns:
                dict
        """
        return self.get('httpmetrics')

    def cpuprof(self):
        """ Used to capture a profile of what Syncthing is doing on the CPU.

            Returns:
                dict
        """
        return self.get('cpuprof')

    def heapprof(self):
        """ Used to capture a profile of what Syncthing is doing with the heap memory.

            Returns:
                dict
        """
        return self.get('heapprof')

    # TODO: needs handling of the resulting .zip
    def support(self):
        """ Collects information about the running instance for troubleshooting purposes. 
            The resulting content-type is 'application/zip'

            Returns a Response object from the Requests module which can be saved using a write buffer.

            Returns:
                object: Response object
            
            >>> sync = _syncthing()
            >>> result = sync.debug.support()
            >>> with open("out.zip", 'wb') as wb:
            >>>    for chunk in result.iter_content():
            >>>        wb.write(chunk)
        """
        return self.get('support', stream=True)

    def file(self, folder, file):
        """ Shows diagnostics about a certain file in a shared folder.

            Args:
                folder (str): Folder ID
                file (str): File relative to the folder path
        """
        return self.get('file', params={'folder': folder, 'file': file})

class Noauth(BaseAPI):
    """ HTTP REST endpoint for Noauth calls."""

    prefix = '/rest/noauth/'

    def health(self):
        """ Returns a dict

            Returns:
                dict: {"status": "OK"}
        """
        return self.get('health')

class Syncthing(object):
    """ Default interface for interacting with Syncthing server instance.

        Args:
            api_key (str)
            host (str)
            port (int)
            timeout (float)
            is_https (bool)
            ssl_cert_file (str)

        Attributes:
            system: instance of :class:`.System`.
            config: instance of :class:`.Config`.
            cluster: instance of :class:`.Cluster`.
            folder: instance of :class:`.Folder`.
            database: instance of :class:`.Database`.
            stats: instance of :class:`.Statistics`.
            misc: instance of :class:`.Misc`.
            debug: instance of :class:`.Debug`.
            noauth:instance of :class:`.Noauth`.

        Note:
            - attribute :attr:`.sys` is an alias of :attr:`.system`
            - attribute :attr:`.conf` is an alias of :attr:`.config`
            - attribute :attr:`.db` is an alias of :attr:`.database`
            
    """

    def __init__(self, api_key, host='localhost', port=8384,
                 timeout=DEFAULT_TIMEOUT, is_https=False, ssl_cert_file=None):

        # save this for deferred api sub instances
        self.__api_key = api_key

        self.api_key = api_key
        self.host = host
        self.port = port
        self.timeout = timeout
        self.is_https = is_https
        self.ssl_cert_file = ssl_cert_file

        self.__kwargs = kwargs = {
            'host': host,
            'port': port,
            'timeout': timeout,
            'is_https': is_https,
            'ssl_cert_file': ssl_cert_file
        }

        self.system = self.sys = System(api_key, **kwargs)
        self.config = self.conf = Config(api_key, **kwargs)
        self.cluster = Cluster(api_key, **kwargs)
        self.folder = Folder(api_key, **kwargs)
        self.database = self.db = Database(api_key, **kwargs)
        self.stats = Statistics(api_key, **kwargs)
        self.misc = Misc(api_key, **kwargs)
        self.debug = Debug(api_key, **kwargs)
        self.noauth = Noauth(api_key, **kwargs)

    def events(self, last_seen_id=None, filters=None, **kwargs):
        kw = dict(self.__kwargs)
        kw.update(kwargs)
        return Events(api_key=self.__api_key,
                      last_seen_id=last_seen_id,
                      filters=filters,
                      **kw)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
