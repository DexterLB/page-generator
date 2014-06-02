#!/usr/bin/python3

class Util(object):
    '''Some utils for working with basic datatypes
    '''
    @staticmethod
    def startsWithTrim(s, v):
        '''if s starts with v, returns s without v.
        Otherwise returns None.
        '''
        if s.startswith(v):
            return s[len(v):]
        return None

    @staticmethod
    def dicAdd(dic, key, val):
        '''adds a value to a dict if it doesn't already have it
        '''
        if key not in dic.keys():
            dic[key] = val

    @staticmethod
    def dicAddNo(dic, key, val, no=None):
        '''adds a value to a dict if it doesn't already have it
        or if the value is not no
        '''
        if not val == no:
            Util.dicAdd(dic, key, val)
