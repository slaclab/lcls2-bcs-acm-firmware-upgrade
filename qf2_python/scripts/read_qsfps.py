#!/usr/bin/env python

import argparse
import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Identify a board and get an interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Only in the runtime
identifier.verifyInRuntime(args.target, args.verbose)

x = identifier.get_active_interface(args.target, args.verbose)

v = x.kintex_qsfp_1_get()

for key, value in v.iteritems():
    print(key, ':', value)

v = x.kintex_qsfp_2_get()

for key, value in v.iteritems():
    print(key, ':', value)

