#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by: Blake on 5/7/2015 at 12:59 PM

import re

from bunch import Bunch

from .interface import Interface, VERB_SWAPS
from .data import rest_md

DOC_TOKEN = '###'
CODE_BLOCK_REGEX = re.compile(r'```.*')
REST_HOOK_REGEX = re.compile(r'###\W+(?P<verb>\S+)\W+(?P<endpoint>.+)', re.I)

METHOD_STRING = '''
{modifier}
def {method}(self, **kwargs):
    """{docstring}"""
    return self._interface.req("rest{endpoint}", "{verb}")'''.strip()

class SyncthingType(type):
    def _make_req(cls, method, endpoint, verb, docstring):
        modifier = '@property' if verb == 'GET' else ''
        return METHOD_STRING.format(
            docstring = docstring,
            modifier = modifier, method = method,
            endpoint = endpoint, verb = verb)

    def __init__(cls, name, bases, clsdict):
        super(SyncthingType, cls).__init__(name, bases, clsdict)

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
            act_pieces = [VERB_SWAPS[verb]] + act.split('/')[1:]
            act_method = '_'.join(filter(lambda x: x != '', act_pieces))

            # generate the code and add it to the object
            code = cls._make_req(act_method, act, verb, docstring)
            exec(code, globals(), clsdict)
            setattr(cls, act_method, clsdict[act_method])


class Syncthing(object, metaclass=SyncthingType):
    def __init__(self, interface):
        self._interface = interface

    @property
    def connected(self): return self._interface.is_connected




