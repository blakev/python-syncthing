#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:59 PM

import re
from functools import wraps

from six import with_metaclass
from bunch import Bunch

from interface import VERB_SWAPS as verb_swap
from data import rest_md

DOC_TOKEN = '###'
CODE_BLOCK_REGEX = re.compile(r'```.*')
REST_HOOK_REGEX = re.compile(r'###\W+(?P<verb>\S+)\W+(?P<endpoint>.+)', re.I)

METHOD_STRING = '''
{modifiers}
def {method}(self, **kwargs):
    """{docstring}"""
    kwargs = self._check_method_warnings("{method}", kwargs)
    return self._interface.req("rest{endpoint}", "{verb}", **kwargs)'''.strip()

# instance-breaking methods defined in the REST-API
WARNING_METHODS = [
    'set_system_reset'
]

class SyncthingType(type):
    def _make_req(cls, method, endpoint, verb, docstring):
        modifier = verb == 'GET'

        modifiers = '@property' if modifier else ''

        x = METHOD_STRING.format(
            docstring = docstring,
            modifiers = modifiers, method = method,
            endpoint = endpoint, verb = verb)

        return x

    def __init__(cls, name, bases, clsdict):
        super(SyncthingType, cls).__init__(name, bases, clsdict)

        if hasattr(cls, 'imported'):
            return

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
            last_doc_find = end_doc + len(DOC_TOKEN)

            # remove all of the code block identifiers, such as bash and json
            docstring = CODE_BLOCK_REGEX.sub('', rest_md[start_doc:end_doc]).strip()

            # remove all the xtra newlines
            docstring = re.sub(r'[\n]+', '\n', docstring)

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
        if method_name not in self._warning_methods:
            return kwargs_obj

        if not kwargs_obj.get('force', False):
            raise UserWarning(method_name + ' is marked as a WARNING_METHOD, to call method pass \'force=True\'.')
        else:
            kwargs_obj.pop('force')
            return kwargs_obj

    def add_warning_method(self, method_name):
        if method_name in self._warning_methods or method_name.startswith('__'):
            return

        if hasattr(self, method_name):
            self._warning_methods.append(method_name)

    def remove_warning_method(self, method_name):
        if method_name in self._warning_methods:
            self._warning_methods.remove(method_name)

    @property
    def connected(self):
        return self._interface.is_connected

    @property
    def warning_methods(self):
        return self._warning_methods

    @property
    def custom_warning_methods(self):
        return set(self._warning_methods).difference(set(WARNING_METHODS))


