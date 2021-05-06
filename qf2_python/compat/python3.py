#!/usr/bin/env python3

def dict_iteritems(s):
    return s.items()

def unicode_chr(s):
    return chr(s)

def print_no_flush(s):
    print(s + ' ', end='', flush=False)

def print_no_return(s):
    print(s + ' ', end='', flush=True)

def str_cast(s):
    return str(s, encoding='utf-8')
    
def my_raw_input(s):
    return input(s)
