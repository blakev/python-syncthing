#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:59 PM

import os
import re
import inspect
from functools import wraps

from six import with_metaclass
from bunch import Bunch

from interface import (
    get_latest_documentation,
    VERB_SWAPS as verb_swap,
    DEFAULT_CACHE_FOLDER, API_FILENAME
)

DOC_TOKEN = '###'
CODE_BLOCK_REGEX = re.compile(r'```.*')
REST_HOOK_REGEX = re.compile(r'###\W+(?P<verb>\S+)\W+(?P<endpoint>.+)', re.I)

METHOD_STRING = '''
{modifiers}
def {method}(self, **kwargs):
    """{docstring}
    """
    kwargs = self._check_method_warnings("{method}", kwargs)
    return self._interface.req("rest{endpoint}", "{verb}", **kwargs)'''.strip()

# instance-breaking methods defined in the REST-API
WARNING_METHODS = [
    'set_system_reset'
]

class SyncthingType(type):
    @staticmethod
    def _make_req(method, endpoint, verb, docstring):
        modifiers = '@property' if verb == 'GET' else ''

        x = METHOD_STRING.format(
            docstring = docstring,
            modifiers = modifiers, method = method,
            endpoint = endpoint, verb = verb)

        return x

    def __init__(cls, name, bases, clsdict):
        super(SyncthingType, cls).__init__(name, bases, clsdict)

        if hasattr(cls, 'imported'):
            return

        ins_file = os.path.join(DEFAULT_CACHE_FOLDER, API_FILENAME % 'latest')

        if not os.path.exists(ins_file):
            ins_file = get_latest_documentation()

        with open(ins_file, 'r') as ins_documentation:
            rest_md = ''.join(ins_documentation.readlines())

        cls.actions = REST_HOOK_REGEX.findall(rest_md)

        # start at the beginning of the MD file for docstring searches
        last_doc_find = 0

        for verb, act in cls.actions:
            # uppercase that HTTP verb
            verb = verb.upper()

            # remove rest from the action for the method/property name
            act = act.lstrip('rest')

            # find the docstring for the given rest endpoint
            start_doc = rest_md.find(DOC_TOKEN, last_doc_find) + len(DOC_TOKEN)
            end_doc = rest_md.find(DOC_TOKEN, start_doc + len(DOC_TOKEN))

            # increment to start at the end of the previous docstring found
            last_doc_find = end_doc

            # remove all of the code block identifiers, such as bash and json
            docstring = CODE_BLOCK_REGEX.sub('', rest_md[start_doc:end_doc]).strip()

            # remove all the extra newlines
            docstring = re.sub(r'[\n]+', '\n', docstring).strip()

            # create the method names
            act_pieces = [verb_swap[verb]] + act.split('/')[1:]
            act_method = '_'.join(filter(lambda x: x != '', act_pieces))

            # generate the code and add it to the object
            code = cls._make_req(act_method, act, verb, docstring)
            exec(code, globals(), clsdict)
            setattr(cls, act_method, clsdict[act_method])

        if not hasattr(cls, 'imported'):
            cls.imported = True


class Syncthing(with_metaclass(SyncthingType, object)):
    def __init__(self, interface):
        self._interface = interface
        self._warning_methods = list(WARNING_METHODS)

    def _check_method_warnings(self, method_name, kwargs_obj):
        """Checker that's executed in each dynamically created method to
        determine if `force=True` and can execute the REST call or not.

        This is used as a stop-gate for methods that may "break" the
        connected Syncthing instance; such as resetting the database.

        Args:
            method_name (str):  The syncthing method to check for `force=True`

            kwargs_obj (dict):  The options for the underlying method, with
                                or without the `force` key. Gets passed directly
                                to the API function's parameters.
        Raises:
            UserWarning

        Returns:
            dict. The reamining arguments for the Syncthing API call sans `force`.

        """
        if method_name not in self._warning_methods:
            return kwargs_obj

        if not kwargs_obj.get('force', False):
            raise UserWarning(method_name + ' is marked as a WARNING_METHOD, to call method pass \'force=True\'.')
        else:
            kwargs_obj.pop('force')
            return kwargs_obj

    def add_warning_method(self, method_name):
        """Adds a warning method from this class, which requires `force=True` to execute.

        Args:
            method_name (str): The syncthing method to apply warning check.

        Returns:
            None.

        """
        if method_name in self._warning_methods or method_name.startswith('__'):
            return

        if hasattr(self, method_name):
            self._warning_methods.append(method_name)

    def remove_warning_method(self, method_name):
        """Removes a method from this class' warning methods, no longer requires `force=True`.

        Args:
            method_name (str): The syncthing method to remove warning check.

        Retuyrns:
            None.

        """
        if method_name in self._warning_methods:
            self._warning_methods.remove(method_name)

    @classmethod
    def help(cls, method_name):
        """Returns the docstring of a dynamically generated method.

        Args:
            method_name (str): The syncthing method to retrieve documentation for.

        Returns:
            __doc__.
        """
        if method_name == '__all__':
            return [x for x in dir(cls) if not x.startswith('__')]

        if hasattr(cls, method_name):
            return inspect.getdoc(getattr(cls, method_name, None))

    @property
    def connected(self):
        """Returns if the underlying interface is connected.

        Returns:
            bool.
        """
        return self._interface.is_connected

    @property
    def methods(self):
        """Returns the available methods after binding from the documentation.

        Returns:
            list.
        """
        return list(filter(lambda x: not x.startswith('_'), dir(self)))

    @property
    def get_methods(self):
        """Returns all the GET methods in the REST API.

        Returns:
            list.
        """
        return [x for x in self.methods if not x.startswith('set_')]

    @property
    def set_methods(self):
        """Returns all the POST methods in the REST API.

        Returns:
            list.
        """
        return [x for x in self.methods if x.startswith('set_') and x != 'set_methods']

    @property
    def warning_methods(self):
        """Returns all the methods which require `force=True` to execute.

        Returns:
            list.
        """
        return self._warning_methods

    @property
    def custom_warning_methods(self):
        """Returns all the warning_methods added programmatically at runtime.

        Returns:
            set.
        """
        return set(self._warning_methods).difference(set(WARNING_METHODS))


