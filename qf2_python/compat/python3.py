#!/usr/bin/env python3

def print_no_flush(s):
    print(s + ' ', flush=False)

def print_no_return(s):
    print(s + ' ', end='', flush=True)

def str_cast(s):
    return str(s, encoding='utf-8')
    
def my_raw_input(s):
    return input(s)
