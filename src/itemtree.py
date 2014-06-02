#!/usr/bin/python3

import os
import re
import configparser
from pprint import pprint as v_d

# local imports:
import glob
import item
import author

class ItemTree(object):
    def __call__(self):
        '''Reads all config files and generates html files! Yay!
        '''
        self.read(glob.fsrc)
        self.buildTree()
        self.assignData()
        self.writeAll()

    def read(self, path):
        '''Reads all config files from a path
        and creates webpage items based on them.
        Each section represents an item.
        '''
        self.items = {}
        self.authors = {}
        filenames = []
        for root, subfolders, files in os.walk(path, followlinks = True):
            for f in files:
                if not f.endswith('.conf'):
                    continue
                filenames.append(os.path.join(root, f))

        cp = configparser.RawConfigParser()
        correct_filenames = cp.read(filenames)
        # TODO: intersect correct_filenames with filenames and display errors
        print('[itemtree] parsed: ', correct_filenames)
        for section in cp.sections():
            values = dict(cp.items(section))
            stype = values.get('type')

            if stype == 'author':
                self.authors[section] = author.Author(
                        section, values)
                continue
            # else, this is a regular item:
            self.items[section] = item.Item(
                    section, values, _items=self.items)


    def buildTree(self):
        '''Builds all items' child/parent relationships'''
        for i in self.items.values():
            for parent in i.parents:
                g = re.match(r'([\@\&]*)(.+)', parent).groups()
                # group 0 is the control characters string
                # group 1 is the name
                parentItem = self.items[g[1]]
                visible = '@' not in g[0]
                i._parents.append(item.Parent(
                    itemObject = parentItem
                    , hasMeVisible = visible
                    , visibleInPathList = '&' not in g[0]))

                parentItem._children.append(item.Child(
                    itemObject = i
                    , visible = visible))

    def assignData(self):
        '''Assigns external data to items.
        Currently just assigns authors.
        '''
        for i in self.items.values():
            i._author = self.authors[i.author]
            i.preprocess()

    def writeAll(self):
        '''Writes all items' output files
        '''
        for i in self.items.values():
            i()


def main():
    tree = ItemTree()
    tree()
    return tree

if __name__ == '__main__':
    tree = main()
    for item in tree.items.values():
        v_d(item.__dict__)
        print(
                "parents: "
                , [parent.item._name for parent in item._parents])
        print(
                "children: "
                , [child.item._name for child in item._children])
        print("\n\n ------------ \n\n")

