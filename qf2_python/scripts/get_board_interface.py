#!/usr/bin/env python3

import argparse

import qf2_python.identifier

parser = argparse.ArgumentParser(description='Identify a board and get a matching interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
parser.add_argument('-d', '--development', action="store_true", help='Development mode - uses the dev_.py interface file instead of looking up a specific file based on the firmware checksum')
args = parser.parse_args()

x = qf2_python.identifier.get_active_interface(args.target, args.verbose, args.development)
