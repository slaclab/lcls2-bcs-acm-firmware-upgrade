#!/usr/bin/env python

import argparse

import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Retreive board and firmware identification information', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

x = identifier.get_board_information(args.target, args.verbose)

for i, j in sorted(x.items()):
    print(i+' : '+j)
