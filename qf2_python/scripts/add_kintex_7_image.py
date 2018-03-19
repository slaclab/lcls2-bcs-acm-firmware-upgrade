#!/usr/bin/env python

import time, sys, argparse
from qf2_python.configuration.jtag import *
from qf2_python.configuration.spi import *

SEQUENCER_PORT = 50003

parser = argparse.ArgumentParser(description='Add Kintex-7 boot image', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', help='Firmware bitfile to add')
parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output')

args = parser.parse_args()

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True),args.verbose)

# Create a Kintex firmware interface
interface = kintex_7_firmware.interface(prom)

# Write the image into available space if possible
interface.add_image(args.bit)
