#!/bin/env python

import argparse, time, datetime
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Display QF2-pre monitors', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')

args = parser.parse_args()

x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

while True:
    print
    print '----------------------------------', datetime.datetime.now(), '----------------------------------'
    x.print_monitors()
    time.sleep(1)

