#!/usr/bin/python3

import os

# local imports
import glob

class Author(object):
    '''Simple class, though resembling item.Item, used for storing author data
    '''
    def __init__(self, _name, values = None):
        '''Create an Author class
        '''
        self._name = _name

        if values:
            self.addValues(values)

    def addValues(self, values):
        '''Parses a dictionary of values into this class' fields
        '''
        self.shortname = values.get('shortname', self._name)
        self.longname = values.get('longname', values.get('name', self.shortname))
        self.url = values.get('url')

        self.meta = values.get('meta', self.longname)
        self.header = values.get('header')
