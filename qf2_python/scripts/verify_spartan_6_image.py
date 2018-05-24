#!/usr/bin/env python

# Alternative way of dealing with python package semantics
# Append package path if it isn't already known
#if __name__ == '__main__' and __package__ is None:
#    import sys, os.path as path
#    print(path.dirname(path.dirname(path.abspath(__file__))))
#    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import argparse, helpers
from ..configuration.jtag import *
from ..configuration.spi import *

parser = argparse.ArgumentParser(description='Verify Spartan-6 image', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', help='Bitfile to compare against')
parser.add_argument('-X', '--bootloader', action="store_true", default=False, help='Verify bootloader')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')
parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

args = parser.parse_args()

# Chose firmware location (bootloader or runtime)
if args.bootloader == True:
    FIRMWARE_SECTOR_OFFSET = 0
else:
    FIRMWARE_SECTOR_OFFSET = 32

SEQUENCER_PORT = int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# If not bitfile provided for comparison, do an integrity check
if args.bit == None:
    print 'No bitfile provided - performing PROM integrity check'
    if ( helpers.prom_integrity_check(prom, FIRMWARE_SECTOR_OFFSET) == 0 ):
        exit(1)
    exit(0)
else:
    print 'Bitfile provided - performing PROM integrity check'
    if ( helpers.prom_compare_check(prom, FIRMWARE_SECTOR_OFFSET, args.bit) == 0 ):
        exit(1)
    exit(0)


