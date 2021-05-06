#!/usr/bin/env python2

import sys

def dict_iteritems(s):
    return s.iteritems()

def unicode_chr(s):
    return unichr(s)

def print_no_flush(s):
    print s,

def print_no_return(s):
    print s,
    sys.stdout.flush()

def str_cast(s):
    return str(s)

def my_raw_input(s):
    return raw_input(s)
