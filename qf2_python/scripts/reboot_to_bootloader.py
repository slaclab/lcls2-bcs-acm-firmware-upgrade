#!/usr/bin/env python3

import argparse, time
import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Reboot to the Spartan bootloader firmware', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
parser.add_argument('-w', '--wait', type=int, default=0, help='Wait time after reboot in seconds')
args = parser.parse_args()

identifier.reboot_to_bootloader(args.target, args.verbose)

time.sleep(args.wait)

