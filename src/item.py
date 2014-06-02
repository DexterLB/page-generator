#!/usr/bin/python3

import os
from operator import attrgetter
from collections import defaultdict

# local imports
import glob
from util import Util

class Item(object):
    '''Holds the data for a webpage item, and provides operations on it'''
    def __init__(self, _name, values = None, filename = None, _items = None):
        '''Create an item
        '''

        self._name = _name
        self._items = _items

        if filename:
            self._fname = filename
            self._fpath = os.path.dirname(self._fname)
        else:
            self._fname = None
            self._fpath = glob.fsrcpath

        if values:
            self.addValues(values)

    def __call__(self):
        pass    # later

    def addValues(self, values):
        '''Parses a dictionary of values into the item's fields'''
        try:
            self.parents = values['parents'].split(' ')
        except KeyError:
            self.parents = []
        self.q_parents = []
        self.q_children = []

        self.urlBasename = self.getUrlBasename(values.get('url'))
        self.url = self.getUrl(self.urlBasename)
        self.outFileBasename = self.getOutFileBasename(values.get('baseoutfile'))
        self.outFile = self.getOutFile(self.outFileBasename)

        self.title = values.get('title', self._name)
        self.description = values.get('description', '')
        self.author = values.get('author', glob.author)

        self.q_author = None

        self.time = int(values.get('time', 0))

        self.sortby = values.get('sortby', 'time title')
        self.sortreverse = (values.get('sortreverse', 'true')) == 'true'

        self.isAFolder = False
        try:
            self.contentfile = os.path.join(self._fpath, values['content'])
            self.text = None
        except KeyError:
            self.contentfile = None
            try:
                self.text = values['text']
            except KeyError:
                self.isAFolder = True

        self.lspic = values.get('lspic')

        # parse all [class_x] values into self.classes.[x]
        self.classes = defaultdict(lambda: [])
        self.classes.update({
            k: v.split(' ') for k, v in map(
                lambda x: (Util.startsWithTrim(x[0], 'class_'), x[1])
                , values.items()
            )
            if k is not None
        })
        Util.dicAddNo(self.classes, 'lsi', self.classes.get('ls'))


        self.badge = (values.get('badge', 'true')) == 'true'

    def getUrlBasename(self, url = None):
        '''Creates a base url (without the main url path) for the item'''
        if not url:
            url = self._name    # maybe md5 hash?
        return url

    def getUrl(self, url = None):
        '''Creates an URL for the item, takes an optional relative URL'''
        return os.path.join(glob.upath, self.getUrlBasename(url))

    def getOutFileBasename(self, filename = None):
        '''Returns the basename of the output file for this item'''
        if not filename:
            filename = self.urlBasename
        return filename

    def getOutFile(self, filename = None):
        '''Returns the full filename of the output file of the item'''
        return os.path.join(glob.fpath, self.getOutFileBasename(filename))

    def paths(self, keepInvisible=False):    # FIXME - convert to recursive
        '''Returns a list of paths for this item.
        Each 'path' is a list of items itself, where the last
        item is this one and moving backwards in it you move
        up in the path tree. Since items can have multiple
        parents each item has multiple paths, hence this is
        a list of paths

        paths -> [[item]]
        '''
        plist = [[self]]    # list of list of items, containing self
        more = True
        while more:
            nlist = []
            more = False    # FIXME
            for p in plist:
                if not p[0].q_parents:
                    nlist.append(p)
                else:
                    for parent in p[0].q_parents:
                        if keepInvisible or parent.visibleInPathList:
                            nlist.append([parent.item] + p)
                            more = True
            plist = nlist
        return plist

    def contentFromFile(self):
        '''Reads the HTML content from self.contentfile
        and returns it as plain text
        '''
        with open(self.contentfile, 'r') as f:
            return f.read()

    def realContent(self):
        '''Returns the HTML content as plain text
        '''
        if self.isAFolder:
            return '<ls />'
        return self.text or self.contentFromFile()

    def sortChildren(self):
        '''Sorts self.q_children as stated by self.sortby
        '''
        self.q_children.sort(
                key=attrgetter(*tuple(map(
                    lambda t: 'item.' + t
                    , self.sortby.split(' ')
                    )))
                , reverse=self.sortreverse)

    def preprocess(self):
        '''Do some stuff to get ready for the actual html generation
        '''
        self.sortChildren()


class Parent(object):
    '''Used to store parent data
        hasMeVisible --> am I visible in this parent's child list
        item --> the actual item of the parent
    '''
    def __init__(self, itemObject, hasMeVisible, visibleInPathList):
        self.item = itemObject
        self.hasMeVisible = hasMeVisible
        self.visibleInPathList = visibleInPathList

class Child(object):
    '''Used to store child data
        visible --> is this child visible from my POV
        item --> the actual item of the child
    '''
    def __init__(self, itemObject, visible):
        self.item = itemObject
        self.visible = visible
