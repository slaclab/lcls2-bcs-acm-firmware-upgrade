#!/usr/bin/env python3

import argparse
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Identify a board and get an interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
args = parser.parse_args()

x = qf2_python.identifier.get_active_interface(args.target)

v = x.kintex_qsfp_1_get()

for key, value in v.iteritems():
    print key, ':', value

