#!/usr/bin/env python

import argparse

import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi

parser = argparse.ArgumentParser(description='Lock Spartan-6 image and configuration', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

args = parser.parse_args()

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=int(args.port), input_select=0, speed=0, noinit=True), args.verbose)

print('Unlocking Bootloader')
prom.unlock()

del prom
