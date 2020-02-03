#!/bin/env python

import argparse, time, ctypes
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Test PMOD C interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Start the class
x = qf2_python.identifier.get_active_interface(args.target, args.verbose)

x.sd_init()
