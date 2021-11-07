#!/usr/bin/env python

import argparse

import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.identifier as identifier

SEQUENCER_PORT = 50003

parser = argparse.ArgumentParser(description='Lock Spartan-6 image and configuration', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
#parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

args = parser.parse_args()

identifier.verifyInBootloader(args.target, args.verbose)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

print('Unlocking PROM')
prom.unlock()

del prom
