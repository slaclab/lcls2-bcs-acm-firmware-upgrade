#!/bin/env python

import argparse

import qf2_python.identifier as identifier

parser = argparse.ArgumentParser(description='Test SD card interface', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')
args = parser.parse_args()

# Require bootloader
identifier.verifyInBootloader(args.target)

# Start the class
x = identifier.get_active_interface(args.target, args.verbose)

# Run SD card initialization
x.sd_init()
