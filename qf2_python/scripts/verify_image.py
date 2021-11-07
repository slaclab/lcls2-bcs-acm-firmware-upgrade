#!/usr/bin/env python

# Alternative way of dealing with python package semantics
# Append package path if it isn't already known
#if __name__ == '__main__' and __package__ is None:
#    import sys, os.path as path
#    print(path.dirname(path.dirname(path.abspath(__file__))))
#    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import argparse

import qf2_python.scripts.helpers as helpers
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi

parser = argparse.ArgumentParser(description='Verify firmware image stored in PROM', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-b', '--bit', default=None, help='Bitfile to compare against')
parser.add_argument('-i', '--image', default='K', type=str, help='Target image')
parser.add_argument('-v', '--verbose', action="store_true", default=False, help='Verbose output')

args = parser.parse_args()

identifier.verifyInBootloader(args.target, args.verbose)

# Deprecated - fixed in current hardware
#parser.add_argument('-p', '--port', default=50003, help='UDP port for JTAG interface')

# Validate the image argument and set the image offsets
if args.image == 'B':
    FIRMWARE_SECTOR_OFFSET = 0
elif args.image == 'R':
    FIRMWARE_SECTOR_OFFSET = 32
elif args.image == 'K':
    FIRMWARE_SECTOR_OFFSET = 65
else:
    raise Exception('Image argument \''+args.image+'\' not a recognized type, choices are B (Bootloader), R (Runtime) or K (Kintex)')

# Fixed in current hardware
SEQUENCER_PORT = 50003 #int(args.port)

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

# If not bitfile provided for comparison, do an integrity check
if args.bit == None:
    print('No bitfile provided - performing PROM integrity check')
    if ( helpers.prom_integrity_check(prom, FIRMWARE_SECTOR_OFFSET, args.verbose) == 0 ):
        exit(1)
    exit(0)
else:
    print('Bitfile provided - performing PROM integrity check')
    if ( helpers.prom_compare_check(prom, FIRMWARE_SECTOR_OFFSET, args.bit, args.verbose) == 0 ):
        exit(1)
    exit(0)


