#!/usr/bin/env python

import argparse
import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Toggle single-bit firmware setting', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
parser.add_argument('-s', '--setting', type=str, required=True, help='Setting name to toggle')
args = parser.parse_args()

print('Setting \"'+args.setting+'\" is now: '+str(identifier.get_active_interface(args.target, args.verbose).toggle_setting(args.setting)))

