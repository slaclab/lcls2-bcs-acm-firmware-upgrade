#!/usr/bin/env python3

import argparse, time
import qf2_python.identifier

parser = argparse.ArgumentParser(description='Identify a board and get an interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
parser.add_argument('-w', '--wait', default='0', help='Wait time in seconds')
args = parser.parse_args()

qf2_python.identifier.reboot_to_runtime(args.target, args.verbose)

time.sleep(int(args.wait))
