#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta

import qf2_python.identifier as identifier
import qf2_python.scripts.helpers as helpers
import qf2_python.configuration.jtag.xilinx_bitfile_parser as xilinx_bitfile_parser
import qf2_python.configuration.jtag.jtag as jtag
import qf2_python.configuration.spi.spi as spi
import qf2_python.configuration.spi.constants as spi_constants

def my_exec_cfg(x, verbose=False):
    ldict = locals()
    exec(x,globals(),ldict)
    return ldict['x'].cfg(verbose)

parser = argparse.ArgumentParser(description='Store Spartan-6 image in PROM', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', default='192.168.1.127', help='Current unicast IP address of board')
parser.add_argument('-c', '--complete', default=False, action="store_true", help='Wipe all Kintex image sectors')
parser.add_argument('-v', '--verbose', default=False, action="store_true", help='Verbose output')

args = parser.parse_args()

identifier.verifyInBootloader(args.target, args.verbose)

# Fixed for current hardware
SEQUENCER_PORT = 50003
FIRMWARE_SECTOR_OFFSET = 65
FIRMWARE_ID_ADDRESS = 64 * spi_constants.SECTOR_SIZE

# Initialise the interface to the PROM
prom = spi.interface(jtag.chain(ip=args.target, stream_port=SEQUENCER_PORT, input_select=0, speed=0, noinit=True), args.verbose)

if args.complete:
    print('Erasing all sectors')
    for i in range(0, 103):
        print(str(i)+'/'+'102')
        prom.sector_erase((i + FIRMWARE_SECTOR_OFFSET) * spi_constants.SECTOR_SIZE)
else:
    print('Erasing first sector of image')
    prom.sector_erase(FIRMWARE_SECTOR_OFFSET * spi_constants.SECTOR_SIZE)

print('Erasing old firmware ID block')
prom.sector_erase(FIRMWARE_ID_ADDRESS)
