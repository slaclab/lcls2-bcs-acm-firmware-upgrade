#!/usr/bin/env python

import argparse, time
import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Read QSFP data', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Target IP address')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

while True:

    print('Rebooting to bootloader')
    identifier.reboot_to_bootloader(args.target, args.verbose)
    time.sleep(30)

    print('Rebooting to runtime')
    identifier.reboot_to_runtime(args.target, args.verbose)
    time.sleep(30)
